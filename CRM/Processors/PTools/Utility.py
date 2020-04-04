from __future__ import division

import json
import random
from datetime import datetime, timedelta
from tempfile import NamedTemporaryFile

from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.http.response import HttpResponseBadRequest
from django.shortcuts import render
from django.template import Context
from django.template.loader import get_template
from django.utils import timezone
from django.utils.translation import ugettext as _
from khayyam.jalali_datetime import JalaliDatetime
from weasyprint import HTML

from CRM import settings
from CRM.Core.CRMConfig import read_config
from CRM.Core.Events import fire_event
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.Core.Charge.Package.ChargePackages import get_next_charge_transfer
from CRM.Processors.PTools.Core.Charge.Service.IPStatic import configure_static_ip_address
from CRM.Processors.PTools.DownloadHandler import respond_as_attachment
from CRM.RAS.MK.Utility import MKUtils
from CRM.Tools.DateParser import parse_date_from_str_to_julian
from CRM.Tools.Misc import get_client_ip
from CRM.Tools.Validators import validate_integer, validate_empty_str
from CRM.context_processors.Utils import check_ajax
from CRM.models import UserCurrentService, UserFiles, HelpDesk, NotifyLog, LoginLogs, Invoice, IBSServiceDiscount, \
    PackageDiscount, IBSService, IBSUserInfo, ServiceProperty, DefaultServiceProperty, FreeTrafficLog, \
    UserProfile, IBSServiceProperties, HelpDepartment, Polls

__author__ = 'Administrator'


def send_error(request, msg):
    if check_ajax(request):
        res = {'msg': msg, 'param': None}
        return HttpResponseBadRequest(json.dumps(res), content_type='text/json')
    return render(request, 'errors/CustomError.html', {'error_message': msg})


def calculate_expire_date(add_days, expire_date):
    try:
        if hasattr(expire_date, 'tzinfo'):
            if expire_date.tzinfo:
                expire_date.activate(settings.TIME_ZONE)
                expire_date = timezone.localtime(expire_date, timezone.get_current_timezone())
        ct = datetime.today()
        exd = expire_date
        if exd is None:
            dif = timedelta(days=add_days)
        else:
            if isinstance(exd, str):
                exd = datetime.strptime(exd, '%Y-%m-%d %H:%M')
            if exd < ct:
                dif = ct - exd
                dif = dif + timedelta(days=add_days)
            else:
                dif = exd + timedelta(days=add_days)
        if isinstance(dif, timedelta):
            dif = datetime.today() + timedelta(days=add_days)
        dif = datetime(year=dif.year, day=dif.day, month=dif.month, hour=12, minute=0, second=0)
        return dif
    except Exception as e:
        print e.message
        return None


def get_user_polls(user_id):
    res = Polls.objects.filter(Q(start_date=None, end_date=None) |
                               Q(start_date=None, end_date__gt=datetime.today().date()) |
                               Q(start_date__lt=datetime.today().date(), end_date__gt=datetime.today().date()) |
                               Q(start_date__lt=datetime.today().date(), end_date=None),
                               is_closed=False, is_deleted=False).distinct()
    res = res.exclude(fk_user_polls_poll__is_finished=True)
    return res


def get_ref_page(request):
    """
    Get the back link for the current request
    :param request:
    :return: str
    """
    assert isinstance(request, HttpRequest)
    ref_page = request.META.get('HTTP_REFERER')
    base_address = read_config('login_base_address', '127.0.0.1')
    if base_address in ref_page:
        return ref_page
    else:
        return base_address


def get_full_sort(get, fields, default_order="-pk"):
    sort = get_sort(get)
    order = default_order
    if sort[0]:
        if sort[0] in fields:
            if 'desc' in sort[1][0]:
                order = '-%s' % sort[0]
            else:
                order = sort[0]
    return order


def get_sort(post):
    if not isinstance(post, dict):
        return None, None
    for p in post.iterkeys():
        if 'sort' in p:
            return p[5: -1], post.getlist(p)
    return None, None


def get_month_expired_users_count():
    try:
        now = JalaliDatetime.today()
        last_month = JalaliDatetime(now.year, now.month - 1, day=now.day)
        next_month = JalaliDatetime(now.year, now.month, day=now.day)
        last_month = last_month.to_datetime()
        next_month = next_month.to_datetime()
        return UserCurrentService.objects.filter(expire_date__lt=next_month, expire_date__gt=last_month).count()
    except Exception as e:
        print e.message
        return 0


def generate_username():
    try:
        pat = read_config('login_pattern', '%Y')
        jd = JalaliDatetime.today()
        pat = jd.strftime(pat)
        rand = random.randint(100, 999)
        pat = pat.replace("RAND", str(rand))
        return pat
    except Exception as e:
        print e.message
        return ''


def init_pager(list_to_page, per_page_res=10, current_page=0, collection_name='data', other_params=None, request=None):
    if validate_integer(current_page):
        paging = get_paging(len(list_to_page), int(current_page), per_page_res)
        next_link = paging['end']
        back_link = paging['back']
        current_page = paging['page']
        page_count = paging['page_count']
        res = list_to_page[paging['start']: paging['end']]
    else:
        paging = get_paging(len(list_to_page), 0, per_page_res)
        next_link = paging['end']
        back_link = paging['back']
        current_page = paging['page']
        page_count = paging['page_count']
        res = list_to_page[paging['start']: paging['end']]

    params = {collection_name: res,
              'next_link': next_link,
              'back_link': back_link,
              'page': current_page,
              'page_count': page_count,
              'request': request,
              'per_page': 30}
    if other_params is not None:
        params.update(other_params)
    return params


def convert_credit(credit, is_bytes=False, use_sign=False):
    try:
        if credit < 5:
            return 0
        if use_sign:
            res = 'KB'
        else:
            res = _('k_byte')
        if is_bytes:
            if credit > 1024:
                credit /= 1024
            if credit > 1024:
                credit /= 1024
                if use_sign:
                    res = 'MB'
                else:
                    res = _('meg')
            if credit > 1024:
                credit /= 1024
                if use_sign:
                    res = 'GB'
                else:
                    res = _('gig')
            credit = float(round(credit, 2))
            return '%s %s' % (credit, res)
        elif credit > 1024:
            if use_sign:
                res = 'GB'
            else:
                res = _('gig')
            credit = '%s %s' % ((round(credit / 1024, 2)), res)
        else:
            if use_sign:
                res = 'MB'
            else:
                res = _('meg')
            credit = '%s %s' % (int(credit), res)
        return credit
    except Exception as e:
        return '0 MB'


def get_new_uploaded_files():
    try:
        return UserFiles.objects.filter(approved=False).count()
    except Exception as e:
        print e.message
        return 0


def get_new_tickets(request):
    try:
        user = request.user
        if not user.is_superuser:
            user_groups = user.groups.all().values_list('pk', flat=True)
            departments = HelpDepartment.objects.filter(group__in=user_groups).values_list('pk', flat=True)
        else:
            departments = HelpDepartment.objects.all().values_list('pk', flat=True)
        return HelpDesk.objects.filter(state__value=0, department__in=departments).count()
    except Exception as e:
        print e.message
        return 0


def get_unread_notify(user_id):
    try:
        return NotifyLog.objects.filter(user=user_id, is_read=False).count()
    except Exception as e:
        print e.message
        return 0


def render_to_pdf(request, template_src, context_dict):
    template = get_template(template_src)
    context = Context(context_dict)
    html = template.render(context)
    f = NamedTemporaryFile(delete=False)
    f.close()
    h = HTML(string=html, encoding='utf-8')
    h.write_pdf(f.name)
    return respond_as_attachment(request, f.name, f.name + '.pdf')


def get_user_invalid_login(user_id):
    if not user_id:
        return 50000
    try:
        dt = datetime.today() - timedelta(hours=1)
        return LoginLogs.objects.filter(user=user_id, date_time=dt).count()
    except Exception as e:
        print e.message
        return 50000


def update_user_credit(fid):
    """
    updates the user credit by invoice ID
    @param fid:invoice number
    @type fid:int
    @return:bool
    @rtype:
    """
    factor = None
    try:
        factor = Invoice.objects.get(pk=fid)
        if factor.is_paid:
            return False
        reduce_one = False
        set_to_active = False
        if factor.user.fk_user_current_service_user.filter().exists():
            if not factor.user.fk_user_current_service_user.get().is_active:  # Service is a test service!
                if factor.extra_data > 1:
                    reduce_one = True
                set_to_active = True
        ibs = IBSManager()
        if factor.service.service_type == 1:
            extra_charge = get_next_charge_transfer(factor.user_id)
        else:
            extra_charge = 0
        if factor.service.service_type == 1:
            replace = True
            if UserCurrentService.objects.filter(user=factor.user_id).exists():
                cs = UserCurrentService.objects.get(user=factor.user_id)
                if factor.service.content_object.fk_ibs_service_properties_properties.get().service_id == cs.service_id:
                    new_service = False
                else:
                    new_service = True
            else:
                new_service = True
        else:
            replace = False
            new_service = False
        if new_service or factor.service.service_type == 1:
            if factor.service.content_object.initial_package > 1:
                if reduce_one:
                    amount = factor.service.content_object.initial_package * (factor.extra_data - 1)
                else:
                    amount = factor.service.content_object.initial_package * factor.extra_data
                if IBSServiceDiscount.objects.filter(
                        service=factor.service.content_object.fk_ibs_service_properties_properties.get().service_id,
                        charge_days=factor.extra_data).exists():
                    amount += IBSServiceDiscount.objects.get(
                        service=factor.service.content_object.fk_ibs_service_properties_properties.get().service_id,
                        charge_days=factor.extra_data).extra_traffic
            else:
                amount = 0
        elif factor.service.service_type == 2:
            amount = factor.service.content_object.amount
            if PackageDiscount.objects.filter(package=factor.service.object_id, is_deleted=False).exists():
                amount += PackageDiscount.objects.get(package=factor.service.object_id,
                                                      is_deleted=False).extended_package
            replace = False
        else:
            return True
        if amount < 1:
            amount = 1
            replace = True  # While user in temp charge, we must set it to clear temp charge state
        uid = factor.user.username
        add_credit = amount
        if set_to_active:
            replace = True
        if not new_service and extra_charge > 0 and not set_to_active:
            add_credit += extra_charge
        ibs.change_credit(add_credit, uid, replace)
        fire_event(7060, factor, None, factor.user_id)
        return True
    except Exception as e:
        if factor:
            fire_event(5616, factor, None, factor.user_id)
        else:
            fire_event(5616, None, None, 1)
        if e.args:
            print (" ".join([str(a) for a in e.args]))
        else:
            print(e.message)
        return False


def assign_user_ip_address(invoice):
    res = configure_static_ip_address(invoice.user_id)
    if res[0]:
        fire_event(3731, invoice, None, invoice.user_id)
    else:
        fire_event(5052, invoice, None, invoice.user_id)
    return res


def update_user_services(fid):
    return


def get_zero_hour():
    return datetime.today() - timedelta(hours=datetime.today().hour, minutes=datetime.today().minute,
                                        seconds=datetime.today().second)


def get_zero_hour_for_day(day):
    return datetime(year=day.year, day=day.day, month=day.month)


def check_user_temp_charge(user_id):
    if not validate_integer(user_id):
        return False
    try:
        ibs = IBSManager()
        user = IBSUserInfo.objects.get(user=user_id)  # User.objects.get(pk=user_id)
        expire_date = ibs.get_expire_date(user.user.username)
        expire_date = parse_date_from_str_to_julian(expire_date)
        credit = ibs.get_user_credit(user.user.username)
        # cs = CurrentService.objects.get(user=user_id).service.period
        if Invoice.objects.filter(user=user.user_id, is_paid=True).exists():
            latest_inv = Invoice.objects.filter(user=user_id, is_paid=True).latest('pay_time').pay_time.date()
        else:
            # Security HOLE! telta time added to check more than today
            latest_inv = datetime.today().date()  # Bug fix for those who did not paid any invoice on new CRM
            latest_inv = latest_inv - timedelta(days=10)
            # print '********************'   + str(type(latest_inv)) + '---' + str(latest_inv)
        if expire_date:
            is_expired = expire_date <= datetime.today()
        else:
            is_expired = True
        low_credit = (credit <= 5 and UserCurrentService.objects.get(user=user_id).service_property.initial_package > 2)
        is_valid_to_charge = not FreeTrafficLog.objects.filter(datetime__gt=latest_inv, user=user_id).exists()
        res = (is_expired and is_valid_to_charge) or (is_valid_to_charge and low_credit)
        return res
    except Exception as e:
        print e.message
        return False


def import_groups_from_ibs(create_new_services=False):
    ibs = IBSManager()
    groups = ibs.get_all_groups()
    for g in groups:
        try:
            create_service_by_group_name(g, create_new_services)
        except Exception as e:
            continue


def create_user_from_ibs(uid, update_mode=False):
    # l = create_logger(None, InfoCodes.creating_ibs_user)
    enter_update_mode = False
    ibs = IBSManager()
    # l.debug("Getting a list of attributes")
    attr = ibs.get_user_info(uid)
    attr = attr[str(uid)]
    password = get_user_info_by_dic(attr, 'normal_password')  # ibs.get_user_password(int(uid))
    u = get_user_info_by_dic(attr, 'normal_username')  # ibs.get_username(uid)
    service = ibs.get_user_service(uid)
    user_is_in_ibs_db = IBSUserInfo.objects.filter(ibs_uid=uid).exists()
    if u is None:
        # l.error("No username is assigned for this user : %s" % uid)
        return False, 1, 'empty username'
    if (update_mode and user_is_in_ibs_db) or User.objects.filter(username=u).exists():
        try:
            if user_is_in_ibs_db:
                # l.debug("User found in IBS DB")
                ibs_id = IBSUserInfo.objects.get(ibs_uid=uid).user.pk
                i_u = User.objects.get(pk=ibs_id)
            else:
                # l.debug("User is NOT in IBS DB")
                i_u = User.objects.get(username=u)
            enter_update_mode = True
            if UserProfile.objects.filter(user__username=u).exists():
                # l.debug("Found User profile : %s" % i_u.pk)
                profile = UserProfile.objects.get(user__username=u)
            else:
                # l.debug("Profile Created for : %s" % i_u.pk)
                profile = UserProfile()
        except Exception as e:
            # if e.args:
                # l.error(" ".join([str(a) for a in e.args]))
            # else:
            #     l.error(e.message)
            # l.error("Unable to create or update user : IBI : %s" % uid)
            return False, 7, 'unable to enter update mode'
    else:
        # l.info("Creating a new user")
        i_u = User()
        profile = UserProfile()
        # l.debug("User and Profile instances created")
        i_u.username = u
    if not i_u.password:
        i_u.set_password(password)
    first_name = get_user_info_by_dic(attr, 'name')
    if not first_name:
        first_name = 'UNKNOWN!'
    if len(first_name) > 30:
        first_name = first_name[0: 30]
    email = get_user_info_by_dic(attr, 'email')
    if not email:
        # l.warning("No email for user : %s" % uid)
        email = '-'
    if not first_name:
        # l.warning("First name is empty for : %s" % uid)
        first_name = '-'
    i_u.first_name = first_name
    i_u.is_active = True
    address = get_user_info_by_dic(attr, 'address')
    if not address:
        address = 'Tehran'
    str_date = get_user_info_by_dic(attr, 'first_login')
    if not str_date:
        date = datetime.today()
    else:
        date = parse_date_from_str_to_julian(str_date)
    i_u.date_joined = date
    profile.address = address
    geo_loc = get_user_info_by_dic(attr, 'custom_field_Geo')
    if not geo_loc:
        geo_loc = '-'
    profile.geo_code = geo_loc
    identity_num = get_user_info_by_dic(attr, 'custom_field_NCode')
    if not identity_num:
        # l.warning("No identity Number for user : %s" % uid)
        identity_num = '-'
    elif len(identity_num) > 10:
        identity_num = identity_num[0: 9]
    profile.identity_number = identity_num
    phone = get_user_info_by_dic(attr, 'phone')
    mobile = get_user_info_by_dic(attr, 'cell_phone')
    profile.comment = get_user_info_by_dic(attr, 'comment')
    if not profile.comment:
        profile.comment = '-'
    # print 'Checking mobile'
    if not mobile:
        mobile = '-'
    elif len(mobile) > 12:
        mobile = mobile[0: 12]
    # print 'Mobile passed'
    # print 'Checking phone'
    if not phone:
        phone = '-'
    elif len(phone) > 15:
        phone = phone[0: 13]
    # print 'phone passed'
    profile.telephone = phone
    profile.mobile = mobile
    birth_data = parse_date_from_str_to_julian(get_user_info_by_dic(attr, 'birthdate'))
    i_u.email = email
    profile.birth_date = birth_data
    try:
        i_u.save()
        profile.user = i_u
        if birth_data:
            profile.birth_date_day = birth_data.day
            profile.birth_date_month = birth_data.month
        else:
            profile.birth_date_day = 1
            profile.birth_date_month = 1
        profile.marriage_date = datetime.today()
        profile.marriage_date_day = 1
        profile.marriage_date_month = 1
        profile.save()
        crm_uid = i_u.pk
        # l.info("User has been updated : %s" % crm_uid)
    except Exception as e:
        # l.error("Saving user data failed for : %s" % uid)
        # if e.args:
        #     l.error(" ".join([str(a) for a in e.args]))
        # else:
        #     l.error(e.message)
        return False, 4, 'unable to create new user'
    try:
        if not user_is_in_ibs_db:
            # l.info("Adding user to IBS DB")
            ibi = IBSUserInfo()
            ibi.ibs_uid = int(uid)
            ibi.user = i_u
            ibi.save()
            # l.info("User added to IBS DB")
    except Exception as e:
        # l.error("Error while trying to add user to IBS DB")
        # if e.args:
        #     l.error(" ".join([str(a) for a in e.args]))
        # else:
        #     l.error(e.message)
        return False, 6, 'unable to assign user to ibs details'
    try:
        # l.debug("Finding if user has any service")
        g_info = IBSService.objects.get(ibs_name=service)
        # i_s = IBSService.objects.get(pk=g_info.service_id)
    except Exception as e:
        # l.error("Error while trying to find a service for user")
        # if e.args:
            # l.error(" ".join([str(a) for a in e.args]))
        # else:
            # l.error(e.message)
        return False, 5, 'unable to find service'
    if enter_update_mode and UserCurrentService.objects.filter(user=crm_uid).exists():
        # l.info("Preparing for updating user service : %s" % uid)
        i_cs = UserCurrentService.objects.get(user=crm_uid)
        if i_cs.service_id != g_info.pk:
            i_cs.service = g_info
            i_cs.service_property = ServiceProperty.objects.get(
                pk=g_info.fk_default_service_property_service.get().default.pk)
    else:
        # l.info("Creating service information for : %s" % uid)
        i_cs = UserCurrentService()
        i_cs.service_property = ServiceProperty.objects.get(
            pk=g_info.fk_default_service_property_service.get().default.pk)
        i_cs.service = g_info
    i_cs.user = i_u
    i_cs.is_active = True
    expire_date = parse_date_from_str_to_julian(get_user_info_by_dic(attr, 'abs_exp_date'))
    if expire_date:
        i_cs.expire_date = expire_date
    try:
        i_cs.save()
        # l.info("User Service data has been saved")
    except Exception as e:
        # l.error("Unable to save user service data : %s" % uid)
        # if e.args:
            # l.error(" ".join([str(a) for a in e.args]))
        # else:
        #     l.error(e.message)
        return False, 6, 'unable to assign service'
    return True, uid, crm_uid


def get_username_from_ras(ip_address, failed_ibs_id):
    try:
        ibs = IBSManager()
        online = ibs.get_user_connection_info_1(failed_ibs_id)
        for o in online:
            try:
                if o[4] == ip_address:
                    ras = o[0]
                    util = MKUtils(ras, read_config('ras_username', 'saeed'),
                                   read_config('ras_password', 'saeed'))
                    return util.get_user_by_ip(ip_address)
            except Exception as e:
                print e.message
                continue
    except Exception as e:
        print e.message


def get_user_name_from_ip(request):
    ibs = IBSManager()
    try:
        ip = get_client_ip(request)
        res = ibs.get_username_from_ip(ip)
        failed = read_config('service_failed_users')
        failed_ids = failed.split(',')
        tmp_res = None
        for f in failed_ids:
            if User.objects.filter(username=res).exists():
                u = User.objects.get(username=res)
                if u.pk == int(f):
                    if IBSUserInfo.objects.filter(user=f).exists():
                        failed_ibs_id = IBSUserInfo.objects.get(user=f).ibs_uid
                    else:
                        failed_ibs_id = ibs.get_user_id_by_username(res)
                    ras_username = get_username_from_ras(ip, int(failed_ibs_id))
                    return ras_username
                else:
                    tmp_res = res
            else:
                return None
        return tmp_res
    except Exception as e:
        print e.message
        res = None
    return res


def build_traffic_by_group_credit(group_info):
    try:
        res = group_info
        if 'raw_attrs' not in res:
            return False
        if 'group_credit' not in res['raw_attrs']:
            gc = 0
        else:
            gc = res['raw_attrs']['group_credit']
            gc = int(float(gc))
        return gc
    except Exception as e:
        print e.args[2]
        return False


def create_service_by_group_name(group_name, create_service=False):
    # l = create_logger(None, "CREATE_IBS_GRP")
    if not validate_empty_str(group_name):
        return False
    try:
        ibs = IBSManager()
        g_info = ibs.get_group_details(group_name)
        if not g_info:
            return False
        gid = g_info['group_id']
        res0 = build_traffic_by_group_credit(g_info)
        if res0 is False:
            # l.warning("Unable to find traffic for group : %s" % group_name)
            res0 = 100
        if not IBSService.objects.filter(ibs_group_id=gid).exists():
            # l.info("Create a new service in CRM")
            new_ibs_group = IBSService()
            new_ibs_group.ibs_group_id = int(gid)
            new_ibs_group.ibs_name = g_info['group_name']
            # new_ibs_group.save()
            new_ibs_group.name = g_info['group_name']
            new_ibs_group.save()
            new_service_property = ServiceProperty()
            new_service_property.initial_package = res0
            new_service_property.name = _('data for ') + new_ibs_group.name
            new_service_property.bandwidth = 128
            new_service_property.base_price = 99999999
            new_service_property.period = 30
            # l.info("Saving original data")
            new_service_property.save()
            default_pr = DefaultServiceProperty()
            default_pr.default = new_service_property
            default_pr.service = new_ibs_group
            default_pr.save()
            ibs_service_pr = IBSServiceProperties()
            ibs_service_pr.service = new_ibs_group
            ibs_service_pr.properties = new_service_property
            ibs_service_pr.save()
            # l.info("Service created : %s" % new_service_property.pk)
            return new_ibs_group.pk
        else:
            # l.info("Attempt to update service information")
            ibg = IBSService.objects.get(ibs_group_id=gid)
            ibg.ibs_name = g_info['group_name']
            # l.info("Service data updated : %s" % ibg.pk)
            # print 'map updated!!!'
            return ibg.pk
            # return -1
    except Exception as e:
        # if e.args:
        #     l.debug(" ".join([str(a) for a in e.args]))
        # else:
        #     l.debug(e.message)
        return False


def get_paging(list_len, start_point, per_page=None):
    if per_page:
        block_count = int(per_page)
        if block_count == 0:
            block_count = 10
    else:
        block_count = 30
    if not validate_integer(list_len):
        return {}
    if not validate_integer(start_point):
        return {}
    if list_len == 0:
        sp = 0
        nx = 0
        p = 1
        pc = 1
        bp = -1
    elif list_len <= block_count:
        sp = 0
        nx = list_len
        p = 1
        pc = 1
        bp = -1
    elif (start_point + block_count) < list_len:
        if start_point == 0:
            sp = 0
        elif start_point == block_count:
            sp = block_count
        elif (start_point % block_count) == 0:
            sp = start_point
        else:
            sp = block_count + int(start_point / block_count) + 1
        nx = sp + block_count
        bp = start_point - block_count
        if bp < 0:
            bp = 0
        pc = int(list_len / block_count) + 1
        if (list_len % block_count) == 0:
            pc -= 1
        p = int((start_point + block_count) / block_count)
    else:
        sp = start_point
        bp = start_point - block_count
        if (list_len % block_count) == 0:
            nx = start_point + block_count
        else:
            nx = start_point + (list_len % block_count)
        p = int((start_point + block_count) / block_count)
        pc = int(list_len / block_count) + 1
        if (list_len % block_count) == 0:
            pc -= 1
    return {'start': sp, 'back': bp, 'page': p, 'page_count': pc, 'end': nx}


def get_user_info_by_dic(user_attr, key_name):
    if not 'attrs' in user_attr:
        return None
    if key_name in user_attr['attrs']:
        return user_attr['attrs'][key_name]
    return None


def insert_new_action_log(request, t_uid, action):
    return 0


def get_upload_unlock(user_id):
    if not user_id:
        return False
    try:
        if UserFiles.objects.filter(user=user_id).filter(approved=1).count() > 8:
            return False
        else:
            return True
    except Exception as e:
        print e.message
        return False

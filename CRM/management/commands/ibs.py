from __future__ import print_function
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.db.models.query_utils import Q
from django.utils.timezone import make_naive, make_aware

from CRM.Core.CRMUserUtils import create_user_in_ibs
from CRM.Core.IBSCharge import ChargePackage, ChargeBasicService
from CRM.IBS.Manager import IBSManager
from CRM.IBS.Users import IBSUserManager
from CRM.Tools.DateParser import parse_date_from_str_to_julian
from CRM.models import Traffic, UserCurrentService, IBSService, ServiceProperty, IBSUserInfo, \
    UserIPStatic, Invoice, IBSServiceDiscount, FloatDiscount, Tower, UserTower


class Command(BaseCommand):
    help = 'Try to Charge N times with different methods'

    def add_arguments(self, parser):
        parser.add_argument('--user', nargs=1, type=int, required=True)
        parser.add_argument('--len', nargs=1, type=int)
        parser.add_argument('--export', action='store_true')
        parser.add_argument('--ipx', action='store_true')
        parser.add_argument('--uin', action='store_true')
        parser.add_argument('--srv', nargs=1, type=int)
        # parser.add_argument('--exp', nargs=1, type=int)
        parser.add_argument('--tms', nargs=1, type=int)
        parser.add_argument('--package', action='store_true')
        parser.add_argument('--psr', action='store_true')
        parser.add_argument('--osr', action='store_true')
        parser.add_argument('--std', action='store_true', help='Set Days For User')
        parser.add_argument('--gcu', action='store_true', help='Get Changed Users')
        parser.add_argument('--ast', action='store_true', help='Assign Users Tower')
        parser.add_argument('--ext', action='store_true',
                            help='Export Towers To Server')
        # parser.add_argument('--package', action='store_true')

    def handle(self, *args, **options):
        user_id = options.get('user')[0]
        package_test = options.get('package')
        package_srv_test = options.get('psr')
        just_service = options.get('osr')
        set_expire_date = options.get('std')
        service_id = options.get('srv')
        gig = options.get('len')
        times = options.get('tms')
        is_export = options.get('export')
        is_export_ip = options.get('ipx')
        update_from_invoice = options.get('uin')
        view_changed = options.get('gcu')
        export_towers = options.get('ext')
        assign_towers = options.get('ast')
        if not times or not times[0]:
            times = 1
        else:
            times = times[0]
        if gig:
            gig = gig[0]
            if not gig:
                gig = 0
        if service_id:
            service_id = service_id[0]
        if package_test:
            self.__change_gig(user_id, gig)
        elif package_srv_test or just_service:
            if not service_id:
                self.stderr("srv is needed")
                return
            if package_srv_test:
                self.__change_gig_with_srv(user_id, service_id)
            elif just_service:
                self.__change_service(user_id, service_id, gig, times)
        elif set_expire_date:
            if not gig:
                self.stderr("len is need")
                return
            self.__expire_user(user_id, gig)
        elif is_export:
            self.__import_to_ibs()
        elif is_export_ip:
            self.__export_ip_address()
        elif update_from_invoice:
            self.__update_from_invoice()
        elif view_changed:
            self.__get_changed_users()
        elif export_towers:
            self.__import_towers()
        elif assign_towers:
            self.__assign_user_towers()

    def __expire_user(self, user_id, days):
        ibs = IBSManager()
        ibs.set_expire_date_by_uid(user_id, days)
        print('[OK]')

    def __change_service(self, user_id, srv, days, times=1):
        x = 0
        while x < times:
            cb = ChargeBasicService(1, user_id)
            ret = cb.update(
                current_service=UserCurrentService.objects.get(user__fk_ibs_user_info_user__ibs_uid=user_id),
                service=ServiceProperty.objects.get(pk=srv), days=days)
            print('TEST : ', x, ret.is_error, ret.message)
            x += 1

    def __change_gig_with_srv(self, user_id, srv):
        x = 0
        while x < 100:
            c = ChargePackage(1, user_id, ChargePackage.CHECK_TYPE_ALL)
            res = c.update(service=IBSService.objects.get(pk=srv), charge_month=1, amount=1024,
                           current_service=UserCurrentService.objects.get(user__fk_ibs_user_info_user__ibs_uid=user_id))
            print('TEST : ', x, ' > ', res.is_error, res.message)
            x += 1

    def __change_gig(self, user_id, amount):
        x = 0
        while x < amount:
            t = Traffic()
            t.amount = 1024
            c = ChargePackage(2, user_id)
            res = c.update(package=t, charge_month=1,
                           current_service=UserCurrentService.objects.get(user__fk_ibs_user_info_user__ibs_uid=user_id))
            print('TEST : ', x, ' > ', res.is_error, res.message)
            x += 1

    def __import_to_ibs(self):
        all_users = IBSUserInfo.objects.all()
        for u in all_users:
            ibs = IBSManager(username='CRM')
            user_id = ibs.get_user_id_by_username(u.user.username)
            if user_id:
                self.__update_ibs_user_service(u.user_id, user_id, False)
            else:
                print('New User Detected : %s' % u.ibs_uid)
                ibs_id = create_user_in_ibs(u.user_id, u.user.username, '123456789')
                self.__update_ibs_user_service(u.user_id, ibs_id, True, True)

    def __update_ibs_user_service(self, user_id, ibs_id, update_expire=False, update_credit=False):
        service = UserCurrentService.objects.filter(user=user_id).first()
        if not service:
            return False
        assert isinstance(service, UserCurrentService)
        ibs = IBSManager(username='CRM')
        if update_expire:
            if service.expire_date:
                self.update_expire_date_by_invoice(user_id)
                # expire_date = make_naive(service.expire_date) - datetime.today()
                # ibs.set_expire_date_by_uid(ibs_id, expire_date.days, True)
        ibs.update_service(ibs_id, service.service.ibs_name)
        if update_credit:
            if service.service.group_type == 1:
                ibs.change_credit_by_uid(5120, ibs_id, True)
        return True

    def __export_ip_address(self):
        ips = UserIPStatic.objects.filter(is_deleted=False, is_reserved=False, ip__isnull=False)
        for i in ips:
            ibs = IBSManager()
            ibm = IBSUserManager(ibs)
            ibs_info = IBSUserInfo.objects.filter(user=i.user_id).first()
            if not ibs_info:
                continue
            assert isinstance(ibs_info, IBSUserInfo)
            print('%s has %s' % (ibm.get_user_ip_static(ibs_info.ibs_uid), ibs_info.ibs_uid))
            #
            # if i.ip_id is None:
            #     continue
            # print('ASSIGNING %s FOR %s' % (i.ip.ip, ibs_info.ibs_uid))
            # ibm.assign_ip_static(ibs_info.ibs_uid, i.ip.ip)

    def update_nearest_exp_date(self):
        users = IBSUserInfo.objects.all()
        for u in users:
            try:
                ibs = IBSManager()
                ibs.set_expire_date_by_uid(u.ibs_uid, 1)
                ibs.set_expire_date_by_uid(u.ibs_uid, -1)
            except Exception:
                pass

    def update_expire_date_by_invoice(self, user_id):
        log = open('/var/CRM/export_ibs.txt', 'a+')
        u = IBSUserInfo.objects.get(user=user_id)
        invoices = u.user.fk_invoice_user.filter(Q(service__service_type=12) |
                                                 Q(service__service_type=1),
                                                 extra_data__gt=0,
                                                 is_paid=True).order_by('pk').last()

        if invoices is None:
            return False
        ibs = IBSManager()
        try:
            expire_date = parse_date_from_str_to_julian(ibs.get_expire_date_by_uid(u.ibs_uid))
        except Exception as e:
            print(e.message or e.args)
            return False
        if expire_date is None:
            return False
        expire_date = make_aware(expire_date)
        if expire_date <= invoices.pay_time:
            ds = FloatDiscount.objects.filter(charge_month=invoices.extra_data).first()
            if ds:
                extra_charges = ds.extra_charge
            else:
                extra_charges = 0
            # to_add = to_add_delta.days
            real_time = invoices.pay_time + timedelta((invoices.extra_data * 30) + extra_charges)
            dt = make_naive(real_time) - datetime.today()
            # to_add_delta = real_time - expire_date
            to_add = dt.days
            if 0 >= to_add >= -2:
                to_add = 2
            elif to_add < -3:
                return False
            ibs.set_expire_date_by_uid(u.ibs_uid, to_add)
            res = 'invoice : %s, expires : %s, paid : %s, real : %s, ADDS : %s\r\n' % \
                  (invoices.pk, expire_date, invoices.pay_time, real_time, to_add)
            log.write(res)
            print(res)

    def __update_from_invoice(self):
        users = IBSUserInfo.objects.all()
        log = open('/var/CRM/export_ibs.txt', 'a+')
        for u in users:
            invoices = u.user.fk_invoice_user.filter(Q(service__service_type=12) |
                                                     Q(service__service_type=1),
                                                     extra_data__gt=0,
                                                     is_paid=True).order_by('pk').last()
            if invoices is None:
                continue
            ibs = IBSManager()
            try:
                expire_date = parse_date_from_str_to_julian(ibs.get_expire_date_by_uid(u.ibs_uid))
            except Exception as e:
                print(e.message or e.args)
                continue
            if expire_date is None:
                continue
            expire_date = make_aware(expire_date)
            if expire_date <= invoices.pay_time:
                ds = FloatDiscount.objects.filter(charge_month=invoices.extra_data).first()
                if ds:
                    extra_charges = ds.extra_charge
                else:
                    extra_charges = 0
                # to_add = to_add_delta.days
                real_time = invoices.pay_time + timedelta((invoices.extra_data * 30)+extra_charges)
                dt = make_naive(real_time) - datetime.today()
                # to_add_delta = real_time - expire_date
                to_add = dt.days
                if 0 >= to_add >= -2:
                    to_add = 2
                elif to_add < -3:
                    continue
                ibs.set_expire_date_by_uid(u.ibs_uid, to_add)
                res = 'invoice : %s, expires : %s, paid : %s, real : %s, ADDS : %s' % \
                      (invoices.pk, expire_date, invoices.pay_time, real_time, to_add)
                log.write(res)
                print(res)

    def __get_changed_users(self):
        users = IBSUserInfo.objects.all()
        for u in users:
            rex = []
            if u.history.count() > 1:
                h = u.history.all().order_by('-action_date').last()
                if h.ibs_uid != u.ibs_uid:
                    print('%s ==> %s' % (u.ibs_uid, h.ibs_uid))
                else:
                    res = ''
                    for s in u.history.all():
                        res += str(s.ibs_uid) + '|'
                    print('SKIPPED : %s %s' % (u.ibs_uid, res))

    def __import_towers(self):
        towers = Tower.objects.all()
        ibs = IBSManager()
        auth = ibs.get_auth_params()
        data = ibs.get_proxy().user_custom_field.getAllCustomFields(auth)
        if 'building' not in data:
            self.stderr.write('Building not found!')
            return
        values = data.get('building').get('allowable_values')
        px = data.get('building')
        to_add = []
        for t in towers:
            if t.name not in values:
                to_add.append(t.name)
        if len(to_add) < 1:
            self.stdout.write('No Differ found!')
            return
        self.stdout.write('%s New Towers Will Write' % len(to_add))
        params = auth.copy()
        params['comment'] = px.get('comment')
        params['mandatory'] = 'false'  # px.get('mandatory')
        params['name'] = px.get('name')
        params['interface_type'] = px.get('interface_type')
        params['value_type'] = px.get('value_type')
        params['description'] = px.get('description')
        params['allowable_values'] = values + to_add
        params['custom_field_id'] = px.get('custom_field_id')
        try:
            ibs.get_proxy().user_custom_field.updateCustomField(params)
        except Exception:
            self.stderr.write('Error : Unable to complete request')

    def __assign_user_towers(self):
        users = UserTower.objects.all()
        self.stdout.write('%s Users to check...' % users.count())
        for u in users:
            try:
                self.stdout.write('Setting %s' % u.pk)
                ibs_id = u.user.fk_ibs_user_info_user.get().ibs_uid
                tower = u.tower.name
                ibs = IBSManager()
                ibu = IBSUserManager(ibs)
                ibu.change_user_custom_field(ibs_id, 'building', tower)
            except Exception:
                self.stderr.write('Error on setting %s' % u.user.pk)


# from CRM.models import UsersPriceList, PriceList
from django.contrib.auth.models import User
from django.db.models import Sum
from django.utils.translation import ugettext as _
from khayyam import JalaliDatetime
from pytz import utc

from CRM.IBS.Manager import IBSManager
from CRM.Tools.DateParser import parse_date_from_str_to_julian
from CRM.Tools.Validators import validate_integer, get_string, get_integer, validate_email, validate_mobile, \
    validate_tel, validate_identity_number
from CRM.models import UserServiceGroup, ServiceGroups, ResellerProfile, UserOwner, Invoice, UserProfile, IBSUserInfo, \
    CompanyData

__author__ = 'Amir'


def assign_all_users_to_price_list(pid):
    try:
        users = User.objects.all().values_list('pk', flat=True)
        for u in users:
            if UserServiceGroup.objects.filter(user=u).exists():
                pl = UserServiceGroup.objects.get(user=u)
            else:
                pl = UserServiceGroup()
            pl.user = User.objects.get(pk=u)
            pl.service_group = ServiceGroups.objects.get(pk=pid)
            pl.save()
    except Exception as e:
        print e.message


def validate_user(uid, rsl=None):
    if not validate_integer(uid):
        return None
    if User.objects.filter(pk=uid).exists():
        if rsl:
            if is_user_owner(rsl, uid):
                return User.objects.get(pk=uid)
            else:
                return None
        return User.objects.get(pk=uid)
    return None


def is_user_owner(rid, uid):
    if not validate_integer(uid):
        return False
    if not validate_integer(rid):
        return False
    return UserOwner.objects.filter(user=uid, owner=rid).exists()


def change_reseller_deposit(rsl, amount, check_negative=False):
    if not validate_integer(rsl):
        return False
    if not validate_integer(amount):
        return False
    if not ResellerProfile.objects.filter(user=rsl).exists():
        return False
    rp = ResellerProfile.objects.get(user=rsl)
    if check_negative:
        max_neg = rp.fk_reseller_profit_option_reseller.max_neg_credit
        current = rp.profit_price
        if current - amount < (max_neg * -1):
            return False
    rp.old_price = rp.profit_price
    rp.profit_price += amount
    rp.save()
    return True


def get_reseller_user_ids(uid, ids=False):
    users = User.objects.filter(fk_user_owner_user__owner=uid)
    if ids:
        return users.values_list('pk', flat=True)
    return users


def get_reseller(request):
    uid = get_integer(request.GET.get('u'))
    if not uid:
        return None
    if request.user.fk_reseller_profile_user.exists() and request.user.pk != uid:
        if not request.user.has_perm('CRM.view_all_reseller_data'):
            return None
    if User.objects.filter(pk=uid, fk_reseller_profile_user__isnull=False).exists():
        return User.objects.get(pk=uid)
    return None


def get_reseller_profile_data(users, uid):
    ids = users.values_list('pk', flat=True)
    now = JalaliDatetime.today().replace(day=1).to_datetime()
    invoices = Invoice.objects.filter(user__in=ids, is_paid=True, pay_time__gte=now.date())
    service_invoices = Invoice.objects.filter(user__in=ids, is_paid=True, pay_time__gte=now.date(),
                                              service__service_type=1)
    package_invoices = Invoice.objects.filter(user__in=ids, is_paid=True, pay_time__gte=now.date(),
                                              service__service_type=2)
    total_services = service_invoices.aggregate(service_price=Sum('price')).get('service_price')
    if total_services is None:
        total_services = 0
    total_packages = package_invoices.aggregate(package_price=Sum('price')).get('package_price')
    if total_packages is None:
        total_packages = 0
    total_prices = invoices.aggregate(total_price=Sum('price')).get('total_price')
    if not total_prices:
        total_prices = 0
    total_invoices = invoices.count()
    total_users = users.count()
    total_invoice_users = invoices.values('user').distinct().count()
    user_profile = ResellerProfile.objects.get(user=uid)
    profit_options = user_profile.fk_reseller_profit_option_reseller
    package_profit = profit_options.package_profit
    service_profit = profit_options.service_profit
    max_negative_credit = profit_options.max_neg_credit
    total_package_price = (total_packages * package_profit) / 100
    total_service_price = (total_services * service_profit) / 100
    current_deposit = user_profile.profit_price
    return {'total_invoice': total_invoices,
            'total_users': total_users,
            'total_price': total_prices,
            'total_service_price': total_service_price,
            'total_package_price': total_package_price,
            'package_profit': package_profit,
            'service_profit': service_profit,
            'max_neg_credit': max_negative_credit,
            'invoice_users': total_invoice_users,
            'reseller_deposit': int(current_deposit)}


def update_user_profile_from_ibs(**kwargs):
    user_id = kwargs.get('user_id')
    attrs = kwargs.get('attrs')
    if not UserProfile.objects.filter(user=user_id).exists():
        profile = UserProfile()
        profile.user_id = user_id
    else:
        profile = UserProfile.objects.get(user=user_id)
    user = User.objects.get(pk=user_id)
    if 'normal_username' in attrs:
        user.username = attrs['normal_username']
    if 'name' in attrs:
        user.first_name = attrs['name']
    if 'email' in attrs:
        user.email = attrs['email']
    user.save()
    if 'custom_field_Geo' in attrs:
        geo_loc = attrs['custom_field_Geo']
    else:
        geo_loc = None
    if not geo_loc:
        geo_loc = '-1'
    if 'custom_field_NCode' in attrs:
        identity_num = attrs.get('custom_field_NCode')
    else:
        identity_num = None
    if not identity_num:
        identity_num = '-1'
    profile.geo_code = geo_loc
    profile.identity_number = identity_num
    address = attrs.get('address')
    if address:
        profile.address = address
    else:
        profile.address = '-'
    phone = attrs.get('phone')
    if phone:
        profile.telephone = phone
    else:
        profile.telephone = '-'
    mobile = attrs.get('cell_phone')
    if mobile:
        profile.mobile = mobile
    else:
        profile.mobile = '-'
    birth = attrs.get('birthdate')
    if birth:
        profile.birth_date = parse_date_from_str_to_julian(birth).replace(tzinfo=utc)
    comment = attrs.get('comment')
    if not comment:
        comment = '-'
    profile.comment = comment
    profile.save()
    return True, None


def update_ibs_user_from_crm(user_id):
    try:
        if not UserProfile.objects.filter(user=user_id).exists():
            return False, _('user profile is not exist')
        profile = UserProfile.objects.get(user=user_id)
        birth = profile.birth_date
        if birth:
            birth = str(birth)
        comment = profile.comment
        if not comment:
            comment = '-'
        attr = {'address': profile.address,
                'email': profile.user.email,
                'normal_username': profile.user.username,
                'phone': profile.telephone,
                'cell_phone': profile.mobile,
                'birthdate_unit': 'gregorian',
                'name': profile.user.first_name,
                'comment': comment
                }
        if birth:
            attr['birthdate'] = birth
        ibs_uid = IBSUserInfo.objects.get(user=user_id).ibs_uid
        # geo = profile.geo_code
        identity = profile.identity_number

        ibs = IBSManager()
        data_to_update = {'custom_field_NCode': identity}
        ibs.update_custom_fields(ibs_uid, data_to_update)
        return ibs.update_user_attr_dic(str(ibs_uid), attr)
    except Exception as e:
        print e.message
        return False


def create_user_in_ibs(user_id, username, password):
    ibs = IBSManager()
    ibs.add_new_user(username, password, 0)
    ib_id = ibs.get_user_id_by_username(username)
    if IBSUserInfo.objects.filter(user_id=user_id).exists():
        ibi = IBSUserInfo.objects.filter(user_id=user_id).first()
    else:
        ibi = IBSUserInfo()
    ibi.ibs_uid = int(ib_id)
    ibi.user_id = int(user_id)
    ibi.save()
    update_ibs_user_from_crm(user_id)
    return ib_id


class CreateUserError(object):
    def __init__(self, msg, error_code):
        self.msg = msg
        self.err_no = error_code

    def msg(self):
        return self.msg

    def error(self):
        return self.err_no


# class UserBasicInfo(object):
    # def __init__(self):


class CreateUser(object):
    def __init__(self, **kwargs):
        self.data = kwargs
        self.er = None

    def _validate_basic_(self, *skip):
        name = get_string(self.data.get('name'))
        address = get_string(self.data.get('address'))
        username = get_string(self.data.get('username'))
        password = get_string(self.data.get('password'))
        mail = get_string(self.data.get('mail'))
        mobile = get_string(self.data.get('mobile'))
        tel = get_string(self.data.get('phone'))
        identity = get_string(self.data.get('identity'))
        gender = get_integer(self.data.get('gender'), True)
        is_active = get_integer(self.data.get('active'), True)
        if not name:
            self.er = CreateUserError(_('please enter name'), 80404)
            return None
        if not address:
            self.er = CreateUserError(_('please enter address'), 82404)
            return None
        if not username:
            self.er = CreateUserError(_('please enter username'), 81404)
            return None
        if not password:
            self.er = CreateUserError(_('please enter password'), 83404)
            return None
        if not validate_email(mail):
            self.er = CreateUserError(_('invalid email'), 84404)
            return None
        if not validate_mobile(mobile):
            self.er = CreateUserError(_('invalid mobile'), 85404)
            return None
        if not validate_tel(tel):
            self.er = CreateUserError(_('invalid phone number'), 86404)
            return None
        if not validate_identity_number(identity):
            self.er = CreateUserError(_('invalid identity number'), 87404)
            return None
        if not gender.is_success():
            self.er = CreateUserError(_('invalid gender'), 87404)
            return None
        u = User()
        p = UserProfile()
        u.username = username
        u.first_name = name
        u.email = mail
        u.is_active = is_active.is_success()
        u.set_password(password)
        p.address = address
        p.gender = gender
        p.identity_number = identity
        p.mobile = mobile
        p.telephone = tel
        p.user = u
        return u, p

    def personnel(self):
        x = self._validate_basic_()
        if self.er is not None:
            return False, self.er
        x[0].is_staff = True
        x[0].is_superuser = False
        x[0].save()
        x[1].save()
        return x[0].pk

    def internet(self):
        x = self._validate_basic_()
        if self.er is not None:
            return False, self.er
        is_dedicated = get_integer(self.data.get('dedicate'))
        is_company = get_integer(self.data.get('company'))
        x[0].save()
        if is_company:
            x[1].is_company = True
            xd = CompanyData()
            xd.user = x[0]
        x[1].save()
        return x[0].pk

    def admin(self):
        x = self._validate_basic_()
        if self.er is not None:
            return False, self.er
        x[0].is_staff = True
        x[0].is_superuser = True
        x[0].save()
        x[1].save()
        return x[0].pk

    def reseller(self):
        pass

    def create_for_reseller(self):
        pass

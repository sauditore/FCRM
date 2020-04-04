import random
import string
from datetime import datetime

from django.contrib.auth.models import User, Group
from django.core.cache import cache
from django.db.models.query_utils import Q
from django.utils.timezone import now
from django.utils.translation import ugettext as _

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.CRMConfig import read_config
from CRM.Core.CRMUserUtils import create_user_in_ibs, update_ibs_user_from_crm
from CRM.Core.EventManager import NewUserRegisterEventHandler, UnlockAccountEventHandler, \
    UserCommentUpdatedEventHandler, UserProfileChanged
from CRM.Core.ServiceGroupManagement import ServiceGroupManagement
from CRM.Core.ServiceManager import UserServiceStatus
from CRM.Core.TowerUtils import get_tower_pk, add_user_to_tower
from CRM.IBS.Manager import IBSManager
from CRM.Processors.PTools.SearchUtils.UserSearchUtils import advanced_search_users
from CRM.Processors.PTools.SearchUtils.UserSearchUtils import build_params_by_get
from CRM.Processors.PTools.Utility import generate_username
from CRM.Tools.Online.status import CACHE_USERS
from CRM.Tools.Validators import validate_mobile, validate_identity_number
from CRM.models import UserProfile, CompanyData, DedicatedUserProfile, UserTower, \
    ResellerProfile, ResellerProfitOption, \
    UserOwner, LockedUsers, IBSUserInfo, PreRegister, VisitorProfile, UserCreator, OneTimePayment, PeriodicPayment


class RegisterRequestManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': PreRegister})
        super(RegisterRequestManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'responsible__username',
                                         'responsible__pk', 'name', 'responsible__first_name',
                                         'mobile', 'telephone', 'tower', 'region', 'gender']})

    def search(self):
        pass

    def update(self, force_add=False):
        is_personal = self.get_bool('ut', default=True)
        name = self.get_str('n', True, max_len=255)
        mobile = self.get_str('m', True, max_len=20)
        telephone = self.get_str('t', True, max_len=20)
        tower = self.get_str('tw', False)
        region = self.get_str('r', False)
        gender = self.get_bool('gn', False, True)
        px = PreRegister()
        px.name = name
        px.mobile = mobile
        px.telephone = telephone
        px.tower = tower
        px.region = region
        px.is_man = gender
        px.personal = is_personal
        px.save()
        NewUserRegisterEventHandler().fire(px, px.name)


class VisitorRequestManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': VisitorProfile})
        super(VisitorRequestManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'user__pk', 'user__first_name', 'user__username']})

    def search(self):
        pass

    def update(self, force_add=False):
        pass

    def checkout(self):
        user = self.get_target_user(True)
        amount = self.get_int('a', True)
        if amount < 0:
            self.error(_('deposit must be more than 0'), True)
        p = VisitorProfile.objects.filter(user=user.pk).first()
        if not p:
            return user.pk
        p.deposit -= amount
        p.last_payment = now()
        p.save()
        return user.pk


class VisitorRegisterManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': User})
        super(VisitorRegisterManager, self).__init__(request, **kwargs)

    def search(self):
        return User.objects.none()

    def update(self, force_add=False):
        name = self.get_str('n', True)
        email = self.get_str('e', True)
        mobile = self.get_str('m', True, max_len=12)
        tel = self.get_str('t', True, max_len=15)
        password = self.get_str('p', True)
        retype = self.get_str('rp', True)
        gender = self.get_bool('gn')
        if password != retype:
            self.error(_('passwords are not match'), True)
        if User.objects.filter(email=email).exists():
            self.error(_('email is exists'), True, 'e')
        u = User()
        u.email = email
        u.username = email
        u.is_staff = True
        u.set_password(password)
        u.first_name = name
        u.save()
        up = UserProfile()
        up.address = '-'
        up.identity_number = '-'
        up.is_visitor = True
        up.mobile = mobile
        up.telephone = tel
        up.user = u
        up.gender = gender
        up.save()
        u.groups.add(read_config('groups_visitor', 14))
        vp = VisitorProfile()
        vp.user_id = u.pk
        vp.deposit = 0
        vp.payment_type = 0
        vp.save()


class UserManager(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': User})
        super(UserManager, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'username', 'first_name', 'email', 'is_active',
                                         'fk_user_profile_user__address', 'fk_user_profile_user__mobile',
                                         'fk_user_profile_user__telephone', 'fk_user_profile_user__is_dedicated',
                                         'fk_user_profile_user__is_company',
                                         'fk_user_current_service_user__service__name',
                                         'fk_user_current_service_user__expire_date',
                                         'fk_ibs_user_info_user__ibs_uid',
                                         'is_staff', 'is_superuser']})

    user_profile = None
    user_password = None
    is_reseller = property(lambda self: self.store.get('atr') == '1')
    is_normal_user = property(lambda self: self.store.get('atn') == '1' or self.store.get('atn') == '3')
    is_company = property(lambda self: self.store.get('atn') == '2')
    is_dedicate = property(lambda self: self.store.get('de') == '1')
    is_visitor = property(lambda self: self.store.get('atr') == '2')
    is_personnel = property(lambda self: self.store.get('ut') == '1')
    is_superuser = property(lambda self: self.store.get('ut') == '2')

    @staticmethod
    def get_online():
        try:
            online_users = cache.get(CACHE_USERS) or None
            if online_users:
                c = len(online_users)
            else:
                c = 0
            return c
        except Exception as e:
            print e.message
            return 0

    @staticmethod
    def can_switch(user, target_user):
        t_user = User.objects.filter(pk=target_user).first()
        if not t_user:
            return False
        if t_user.is_staff and t_user.is_superuser and user.has_perm('CRM.switch_to_admin'):
            return True and user.has_perm('CRM.switch_account')
        elif t_user.is_staff and user.has_perm('CRM.switch_to_staff'):
            return True and user.has_perm('CRM.switch_account')
        elif user.has_perm('CRM.switch_account'):
            return True
        else:
            return False

    def request_can_switch(self):
        if self.req.session.get('normal_id'):
            return False
        return self.can_switch(self.requester, self.get_target_user(True).pk)

    def switch_user(self):
        target = self.get_target_user(True)
        res = self.can_switch(self.requester, target.pk)
        if res and not self.req.session.get('normal_id'):
            self.req.session['normal_id'] = self.requester.pk
            self.req.session['target_id'] = target.pk
            return True
        return False

    @staticmethod
    def get_personnel_count():
        users = User.objects.filter(is_staff=True, is_active=True, is_superuser=False)
        return users.count()

    def unlock_account(self):
        user = self.get_target_user(True)
        locked = LockedUsers.objects.filter(user=user.pk).first()
        if locked:
            if locked.ibs_locked:
                ibs = IBSManager()
                ibi = IBSUserInfo.objects.get(user=user.pk).ibs_uid
                dt = datetime.today().date() - locked.lock_date.date()
                x = UserServiceStatus(user.pk)
                a = datetime.today().date() - x.current_service.expire_date.date()
                to_add = a.days
                if to_add < 0:
                    to_add = a.days * (-1)
                if dt.days > 20:
                    ibs.set_expire_date_by_uid(ibi, to_add, True)
                # fire_event(4237, user, None, self.requester.pk)
                ibs.unlock_user(ibi)
            locked.delete()
        user.is_active = True
        user.save()
        UnlockAccountEventHandler().fire(user, None, self.requester, True)
        return True

    def get_locked_reason(self):
        u = self.get_target_user(True)
        x = u.fk_locked_users_user.first()
        return x

    def update_comment_inline(self):
        self.get_single_pk(True)
        v = self.get_str('value', True)
        p = self.get_profile()
        p.comment = v
        p.save()
        if self.current.fk_ibs_user_info_user.exists():
            update_ibs_user_from_crm(p.user_id)
        UserCommentUpdatedEventHandler().fire(p.user, v, self.requester, True)

    def search(self):
        ts = self.get_str('iTMS')
        res = User.objects.all()
        if ts:
            ibs_id = self.get_int('iTMS')
            user_id = self.get_int('iTMS')
            if ibs_id:
                res = res.filter(Q(fk_ibs_user_info_user__ibs_uid=ibs_id) |
                                 Q(pk=user_id) |
                                 Q(fk_user_profile_user__mobile__icontains=ts) |
                                 Q(fk_user_profile_user__telephone__icontains=ts)
                                 )
            else:
                res = res.filter(Q(first_name__icontains=ts) |
                                 Q(username__icontains=ts)

                                 )
        else:
            data = build_params_by_get(self.store)
            res = advanced_search_users(**data)
        sp = self.get_search_phrase()
        if self.reseller:
            res = res.filter(fk_user_owner_user__owner=self.reseller)
        if not self.has_perm('CRM.view_admins') or not self.requester.is_superuser:
            res = res.filter(is_superuser=False)
        if not self.has_perm('CRM.view_personnel'):
            res = res.filter(is_staff=False)
        if sp:
            res = res.filter(first_name__icontains=sp)
        return res

    def update(self, force_add=False):
        xx = self.get_single_pk(False)
        if xx:
            return xx
        username = self.get_str('u')
        password = self.get_str('p')
        re_type = self.get_str('rp')
        e_mail = self.get_str('e', True)
        first_name = self.get_str('fn', True)
        activate = self.get_bool('ca', False, False)
        if not username:
            username = generate_username()
        if not password:
            password = ''.join(random.choice(string.lowercase) for i in range(5))
        if not re_type:
            re_type = password
        if password != re_type:
            return self.error(_('passwords are not match'), True)
        if User.objects.filter(username__iexact=username).exists():
            return self.error(_('username is exists'), True, 'u')
        u = User()
        u.username = username
        u.set_password(password)
        u.first_name = first_name
        u.email = e_mail
        u.is_active = activate
        u.last_login = datetime.today()
        u.save()
        self.user_password = password
        self.__dict__['current_object'] = u
        ow = UserCreator()
        ow.user = u
        ow.creator = self.requester
        ow.save()
        if self.reseller:
            ox = UserOwner()
            ox.user = u
            ox.owner = self.requester
            ox.save()
        return u
        # is_company = get_string(store.get('co')) == '1'
        # is_dedicate = get_string(store.get('de')) == '1'

    def set_personnel(self):
        if self.current:
            x = self.current
        else:
            x = self.get_target_user(True)
        x.is_staff = True
        x.save()

    def unset_personnel(self):
        if self.current:
            x = self.current
        else:
            x = self.get_target_user(True)
        x.is_staff = False
        x.save()

    def set_superuser(self):
        if not self.current:
            x = self.current
        else:
            x = self.get_target_user(True)
        x.is_superuser = True
        x.is_staff = True
        x.save()

    def unset_superuser(self):
        if self.current:
            x = self.current
        else:
            x = self.get_target_user(True)
        x.is_superuser = False
        x.save()

    def active_account(self):
        self.current.is_active = True

    def de_active_account(self):
        self.current.is_active = False

    def create_profile(self):
        validate_data = not (self.get_str('ivl', default='0') == '0' and self.requester.is_staff )
        validate_data = validate_data and not self.is_personnel
        mobile = self.get_str('m', validate_data, max_len=15, min_len=10)
        if self.is_company:
            personal_identity = '-'
        else:
            # if self.requester.is_staff:
            personal_identity = self.get_str('idn', validate_data, '-', min_len=10)
            if not validate_identity_number(personal_identity) and validate_data:
                return self.error(_('please enter a valid identity number'), True, 'idn')
            # else:
            #     personal_identity = '-'
        name = self.get_str('fn', validate_data, max_len=50, default='-', min_len=3)
        address = self.get_str('ad', validate_data, default='-', min_len=10)
        telephone = self.get_str('ph', validate_data, max_len=12, default='-', min_len=8)
        comment = self.get_str('des', False, default='--')
        gender = self.get_str('gn', False, '0', 1) == '0'
        mail = self.get_str('eml', validate_data, default='-', min_len=5)
        birth = self.get_date('b', not self.is_company and validate_data, True)
        marriage = self.get_date('mrd', False, True)
        father_name = self.get_str('ftn', not self.is_company and validate_data,
                                   '-', 100, min_len=3)
        sh_number = self.get_str('shn', not self.is_company and validate_data, '-', 20, min_len=1)
        if not validate_mobile(mobile) and not self.is_company and validate_data:
            return self.error(_('please enter mobile number'), True, 'm')
        if not telephone and not self.is_company and validate_data:
            return self.error(_('please enter phone number'), True, 'ph')
        if not personal_identity:
            return self.error(_('please enter identity number'), True, 'idn')
        if not address:
            return self.error(_('please enter address'), True, 'ad')
        if not comment:
            comment = '-'
        if self.current is None:  # If user is new, then current is not None! else current is none and we need to get!
            ux = self.get_target_user(True)
        else:
            return self.error(_('invalid user'), True, 'u')
        if UserProfile.objects.filter(user=ux.pk).exists():
            up = UserProfile.objects.get(user=ux.pk)
        else:
            up = UserProfile()
            up.user_id = ux.pk
        up.mobile = mobile
        up.telephone = telephone
        up.gender = gender
        up.address = address
        up.comment = comment
        up.identity_number = personal_identity
        up.birth_date = birth
        if birth:
            up.birth_date_day = birth.day
            up.birth_date_month = birth.month
        else:
            up.birth_date_day = 0
            up.birth_date_month = 0
        if marriage:
            up.marriage_date = marriage
            up.marriage_date_day = marriage.day
            up.marriage_date_month = marriage.month
        else:
            up.marriage_date = None
            up.marriage_date_day = 0
            up.marriage_date_month = 0
        if self.has_perm('CRM.change_companydata') or self.has_perm('CRM.add_companydata'):
            up.is_company = self.is_company
        if self.has_perm('CRM.add_visitorprofile') or self.has_perm('CRM.change_visitorprofile'):
            up.is_visitor = self.is_visitor
        if self.has_perm('CRM.add_resellerprofile') or self.has_perm('CRM.change_resellerprofile'):
            up.is_reseller = self.is_reseller
        if self.has_perm('CRM.add_dedicateduserprofile') or self.has_perm('CRM.change_dedicateduserprofile'):
            up.is_dedicated = self.is_dedicate
        ux.first_name = name
        up.father_name = father_name
        up.sh_number = sh_number
        up.name = name
        ux.email = mail
        if not self.requester.is_staff:
            up.validation_state = 1
            UserProfileChanged().fire(up, _('edit profile'), self.requester.pk)
        else:
            if self.get_str('ivl', default='0') == '1':
                up.validation_state = 2
            elif self.get_str('ivl', default='0') == '0':
                up.validation_state = 0
        ux.save()
        up.save()
        self.user_profile = up
        return up

    def get_profile(self):
        try:
            if self.user_profile is not None:
                return self.user_profile
            if UserProfile.objects.filter(user=self.current.pk).exists():
                self.user_profile = UserProfile.objects.get(user=self.current.pk)
                return self.user_profile
            return self.error(_('no such profile found'), True)
        except Exception as e:
            return self.error(e.message, True)

    def set_company(self):
        if not (self.has_perm('CRM.change_companydata') and self.has_perm('CRM.add_companydata')):
            return
        self.get_profile()
        company_identity = self.get_str('cs', not self.requester.is_staff, 50)
        company_postal = self.get_str('cz', not self.requester.is_staff, 50)
        company_eco_code = self.get_str('ce', not self.requester.is_staff, 50)
        company_reg = self.get_str('cr', not self.requester.is_staff, 50)
        tx = self.get_profile().user_id
        if CompanyData.objects.filter(user=tx).exists():
            data = CompanyData.objects.get(user=tx)
        else:
            data = CompanyData()
            data.user_id = tx
        # self.user_profile.is_company = True
        data.economic_code = company_eco_code
        data.identity_code = company_identity
        data.registration_number = company_reg
        data.zip_code = company_postal
        data.save()
        # self.user_profile.save()

    def unset_company(self):
        self.get_profile()
        self.user_profile.is_company = False
        self.user_profile.save()

    def set_dedicate(self):
        contact = self.get_str('ds', True)
        self.get_profile()
        if DedicatedUserProfile.objects.filter(user=self.user_profile.user_id).exists():
            du = DedicatedUserProfile.objects.get(user=self.user_profile.user_id)
        else:
            du = DedicatedUserProfile()
            du.user_id = self.user_profile.user_id
        du.contact = contact
        du.save()
        self.user_profile.is_dedicated = True
        self.user_profile.save()

    def unset_dedicate(self):
        self.get_profile()
        self.user_profile.is_dedicated = False
        self.user_profile.save()

    def set_tower(self):
        tower = get_tower_pk(self.store.get('tow'))
        if not tower:
            return
        if UserTower.objects.filter(user=self.current.pk).exists():
            ut = UserTower.objects.get(user=self.current.pk)
        else:
            ut = UserTower()
            ut.user_id = self.current.pk
        ut.tower = tower
        ut.save()
        add_user_to_tower(self.current.pk, tower)
        return ut

    def activate_internet(self):
        if self.current.is_active:
            if not self.user_password:
                self.user_password = ''.join(random.choice(string.lowercase) for i in range(5))
                self.current.set_password(self.user_password)
            create_user_in_ibs(self.current.pk, self.current.username, self.user_password)
            return True
        return False

    def add_to_customer_group(self):
        gid = read_config('groups_customer', 1)
        if not Group.objects.filter(pk=gid).exists():
            return False
        self.current.groups.add(Group.objects.get(pk=gid))
        return True

    def add_to_reseller(self):
        gid = read_config('groups_reseller', 3)
        if not Group.objects.filter(pk=gid).exists():
            return False
        self.current.groups.add(Group.objects.get(pk=read_config('groups_reseller', 3)))
        return True

    def create_reseller(self):
        x = self.get_target_user(True)
        reseller_package_profit = self.get_int('rpp', False, 0)
        reseller_neg_price = self.get_int('rmn', False, 0)
        reseller_service_profit = self.get_int('rsp', False, 0)
        if ResellerProfile.objects.filter(user=x.pk):
            reseller = ResellerProfile.objects.get(user=x.pk)
        else:
            reseller = ResellerProfile()
            reseller.user_id = self.get_target_user(True).pk
            reseller.save()
        if ResellerProfitOption.objects.filter(reseller=reseller.pk).exists():
            options = ResellerProfitOption.objects.get(reseller=reseller.pk)
        else:
            options = ResellerProfitOption()
        options.package_profit = reseller_package_profit
        options.max_neg_credit = reseller_neg_price
        options.service_profit = reseller_service_profit
        options.reseller_id = reseller.pk
        options.save()
        # self.user_profile.is_reseller = True
        # self.user_profile.save()

    def add_to_service_group(self):
        sm = ServiceGroupManagement(self.req, store=self.store)
        sm.pk_name = 'sg'
        try:
            sm.assign_user(self.current.pk)
        except Exception as e:
            self.error(e.message, True)

    def add_to_dedicate_group(self):
        default_dedicated = int(read_config('groups_dedicated', 2))
        self.current.groups.add(Group.objects.get(pk=default_dedicated))

    def remove_from_dedicated_group(self):
        default_dedicated = int(read_config('groups_dedicated', 2))
        self.current.groups.remove(default_dedicated)

    def get_by_ibs(self, ibs):
        if self.requester.is_staff:
            x = self.get_int(ibs)
        else:
            return User.objects.get(pk=self.requester.pk)
        return User.objects.filter(fk_ibs_user_info_user=x).first()

    def create_visitor(self):
        x = self.get_target_user(True)
        vp = VisitorProfile.objects.filter(user=x.pk).first()
        if not vp:
            vp = VisitorProfile()
            vp.user_id = x.pk
            vp.deposit = 0
        vp.payment_type = self.get_int('vpt', False, 0)
        vp.save()

    def remove_visitor(self):
        self.get_profile()
        gid = read_config('groups_visitor', 5)
        self.current.groups.remove(gid)
        self.get_profile().is_visitor = False
        self.user_profile.save()

    def add_to_visitor(self):
        self.get_profile()
        gid = read_config('groups_visitor', 5)
        self.current.groups.add(gid)
        self.user_profile.is_visitor = True
        self.user_profile.save()

    def remove_reseller(self):
        x = self.get_profile()
        x.is_reseller = False
        x.save()
        u = self.get_target_user(True)
        u.groups.remove(read_config('groups_reseller', 3))

    def change_owner(self):
        user = self.get_target_user(True)
        self.pk_name = 'o'
        owner = self.get_single_pk(False)
        if not owner:
            self.pk_name = 'v'
            owner = self.get_single_pk(True)
        user_owner = UserOwner.objects.filter(user=user.pk).first()
        if not user_owner:
            user_owner = UserOwner()
            user_owner.user = user
        user_owner.owner = owner
        user_owner.save()
        if owner.fk_user_profile_user.is_visitor:
            tp = self.get_int('rps', default=0)
            if tp == 0:
                one = OneTimePayment.objects.filter(user=user.pk).first()
                if not one:
                    one = OneTimePayment()
                    one.user = user
                    one.visitor = owner
                    one.save()
                PeriodicPayment.objects.filter(user=user.pk).delete()
            elif tp == 1:
                p = PeriodicPayment.objects.filter(user=user.pk).first()
                if not p:
                    p = PeriodicPayment()
                    p.user = user
                    p.visitor = owner
                    p.save()
                OneTimePayment.objects.filter(user=user.pk).delete()
            else:
                self.error(_('invalid payment type'), True)

    def roll_back(self):
        if self.current:
            self.current.delete()

from __future__ import unicode_literals, division

from audit_log.models.managers import AuditLog
from celery.worker.strategy import default
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.generic import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

from CRM.Core.ModelManager import OwnerManager, AutoUUIDField, CRMManager


class Traffic(models.Model):
    traffic_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100L, db_index=True)
    amount = models.IntegerField(default=1024)
    description = models.CharField(max_length=250L, blank=True)
    is_deleted = models.BooleanField(default=False)
    price = models.FloatField(default=0)
    history = AuditLog()

    class Meta(object):
        db_table = 'packages'
        permissions = (('view_packages', 'View CRM Packages'),
                       )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('view all traffics'), self.pk)


class PackageDiscount(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, db_index=True)
    extended_package = models.IntegerField()
    price_discount = models.IntegerField()
    package = models.ForeignKey(Traffic, related_name='fk_package_discount')
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'package_discount'
        permissions = (('view_package_discount', 'View All Package Discounts'),
                       )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('view_all_package_discount'), self.pk)


class RAS(models.Model):
    id = models.AutoField(primary_key=True)
    ras_name = models.CharField(max_length=200, db_index=True)
    ip_address = models.CharField(max_length=20, db_index=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'ras'

    def __unicode__(self):
        return self.ras_name

    def __str__(self):
        return self.ras_name

    @staticmethod
    def get_url():
        return None


class FreeTrafficLog(models.Model):
    free_traffic_id = models.AutoField(db_column='Free_Traffic_ID', primary_key=True)
    recharger = models.ForeignKey(User, related_name='fk_free_traffic_log_recharger_user')
    datetime = models.DateTimeField(db_index=True)
    user = models.ForeignKey(User, related_name='fk_free_traffic_log_user_user')
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'free_traffic_logs'
        permissions = (('free_traffic', 'One time free charge'),
                       ('double_free_traffic', 'Double free charge'),
                       ('unlimited_charge', 'Unlimited Free Charge'),
                       ('view_temp_charge_report', 'View Temp Charge Report')
                       )

    def __unicode__(self):
        return self.subscriber

    def __str__(self):
        return str(self.pk)

    def get_url(self):
        return '%s?pk=%s' % (reverse('temp_charge_report'), self.pk)


class HelpDeskState(models.Model):
    state_id = models.AutoField(primary_key=True)
    name = models.TextField()
    description = models.TextField(db_column='Description', blank=True)
    value = models.IntegerField(db_index=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'help_desk_state'

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class HelpDepartment(models.Model):
    help_department_id = models.AutoField(primary_key=True)
    department_name = models.CharField(max_length=200, db_index=True)
    group = models.ForeignKey(Group, related_name='fk_help_department_group')
    history = AuditLog()

    class Meta(object):
        db_table = 'help_departments'
        permissions = (('view_help_departments', 'View Help Desk Departments'),
                       )

    def __str__(self):
        return self.department_name

    def __unicode__(self):
        return self.department_name

    def get_url(self):
        return '%s?pk=%s' % (reverse('show all help desk department'), self.pk)


class HelpDesk(models.Model):
    help_desk_id = models.AutoField(primary_key=True)
    title = models.TextField()
    state = models.ForeignKey(HelpDeskState, related_name='fk_help_desk_state',
                              db_index=True)
    user = models.ForeignKey(User, related_name='fk_help_desk_user')
    department = models.ForeignKey(HelpDepartment, related_name='fk_help_desk_department')
    create_time = models.DateTimeField(null=True, db_index=True)
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'help_desk'
        permissions = (('view_help_desk', 'View Help Desk'),
                       )

    def __unicode__(self):
        return self.title

    def __str__(self):
        return self.title

    def get_url(self):
        return '%s?pk=%s' % (reverse('show all tickets'), self.pk)


class LoginLogs(models.Model):
    log_id = models.AutoField(primary_key=True)
    ip_address = models.CharField(max_length=45L, db_index=True)
    date_time = models.DateTimeField(auto_now=True, db_index=True)
    state = models.BooleanField(default=False, db_index=True)
    user = models.ForeignKey(User, related_name='fk_login_logs_user')
    objects = OwnerManager()

    class Meta(object):
        db_table = 'login_logs'

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username

    @staticmethod
    def get_url():
        return None


class NotifyLog(models.Model):
    notify_log_id = models.AutoField(primary_key=True)
    description = models.CharField(max_length=2000L, blank=True, db_index=True)
    user = models.ForeignKey(User, related_name='fk_notify_log_user')
    send_time = models.DateTimeField(db_index=True)
    target = models.CharField(max_length=200, db_index=True)
    result = models.BooleanField(default=False, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    notify_type = models.IntegerField()
    history = AuditLog()

    class Meta(object):
        db_table = 'notify_log'
        permissions = (('view_notification', 'View notifications'),
                       ('send_notification', 'Send Notifications'),)

    def __unicode__(self):
        return self.description

    def __str__(self):
        return self.description

    def get_url(self):
        return '%s?pk=%s' % (reverse('show_all_notifies'), self.pk)


# V2
class GiftHistory(models.Model):
    id = models.AutoField(primary_key=True)
    target_user = models.ForeignKey(User, related_name='fk_gift_history_target_user')
    gift_time = models.DateTimeField(auto_now=True)
    extended_days = models.IntegerField(default=0)
    extended_package = models.IntegerField(default=0)
    history = AuditLog()

    class Meta(object):
        db_table = 'gift_history'
        permissions = (('send_gift', 'Can Send gift for users'),
                       )

    def __str__(self):
        return self.target_user.username

    def __unicode__(self):
        return self.target_user.username

    @staticmethod
    def get_url():
        return None


# V2
class ServiceProperty(models.Model):
    id = models.AutoField(primary_key=True)
    base_price = models.IntegerField(default=9999999)
    initial_package = models.IntegerField(default=1024)
    is_vip_property = models.BooleanField(default=False)
    is_visible = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    package_price = models.IntegerField(default=5000)
    description = models.CharField(max_length=255)
    bandwidth = models.CharField(max_length=100)
    name = models.CharField(max_length=255, db_index=True)
    period = models.IntegerField(default=30)
    start_date = models.DateTimeField(null=True)
    end_date = models.DateTimeField(null=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'service_properties'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('show_all_service_properties'), self.pk)


# V2
class IBSService(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, null=True)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=500)
    ibs_name = models.CharField(max_length=255)
    is_visible = models.BooleanField(default=False)
    # is_vip = models.BooleanField(default=False)   # Removed in Version 2.1
    ibs_group_id = models.IntegerField()
    is_deleted = models.BooleanField(default=False)
    # Added on Float Services
    group_type = models.IntegerField(default=1)  # 1 : Limited, 2 : Unlimited
    history = AuditLog()

    class Meta(object):
        db_table = 'ibs_services'
        permissions = (('import_services', 'Import Services'),
                       ('view_services', 'View All Services'),
                       ('view_credit_report', 'View Credit Report'),
                       ('view_online_users', 'View Online Users'),
                       ('view_connection_log', 'View Connection Log'),
                       ('disconnect_user', 'Disconnect User Service'),
                       ('view_service_summery', 'View Service Summery')
                       )

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('show all services'), self.pk)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


# V2
class DefaultServiceProperty(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(IBSService, related_name='fk_default_service_property_service')
    default = models.ForeignKey(ServiceProperty, related_name='fk_default_service_property_default')
    history = AuditLog()

    class Meta(object):
        db_table = 'default_service_property'

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)

    def get_url(self):
        return '%s?pk=%s' % (reverse('show all services'), self.pk)


# V2
class IBSServiceProperties(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(IBSService, related_name='fk_ibs_service_properties_service')
    properties = models.ForeignKey(ServiceProperty, related_name='fk_ibs_service_properties_properties')
    history = AuditLog()

    class Meta(object):
        db_table = 'ibs_service_properties'

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return unicode(self.pk)

    def get_url(self):
        return '%s?s=%s' % (reverse('show_all_service_properties'), self.service_id)


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    description = models.TextField(blank=True)
    time = models.DateTimeField()
    help_desk = models.ForeignKey(HelpDesk, related_name='fk_ticket_help_desk')
    history = AuditLog()

    class Meta(object):
        db_table = 'ticket'
        permissions = (('view_ticket', 'View Users Ticket'),)

    def __unicode__(self):
        return self.description

    def __str__(self):
        return self.description

    def get_url(self):
        return '%s?pk=%s' % (reverse('ticket details'), self.pk)


class UserFiles(models.Model):
    file_id = models.AutoField(primary_key=True)
    filename = models.TextField(max_length=700)
    approved = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='fk_User_files_user')
    upload_time = models.DateTimeField()
    upload_name = models.CharField(max_length=200)
    objects = OwnerManager()

    class Meta(object):
        db_table = 'user_docs'
        permissions = (('view_files', 'View Uploaded Files'),
                       ('accept_files', 'Accept Uploaded Documents'),
                       ('upload_files', 'Ability to upload Files'),
                       )

    def __str__(self):
        return self.filename

    def __unicode__(self):
        return self.filename

    def get_url(self):
        return '%s?pk=%s' % (reverse('manage_uploads'), self.pk)


class IBSUserInfo(models.Model):
    info_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='fk_ibs_user_info_user')
    ibs_uid = models.IntegerField(db_index=True)
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'ibs_user_info'
        permissions = (('update_user_service', 'Update User Service'),)

    def __str__(self):
        return str(self.ibs_uid)

    def __unicode__(self):
        return str(self.ibs_uid)

    def get_url(self):
        return '%s?pk=%s' % (reverse('show user navigation menu'), self.user_id)


class Solutions(models.Model):
    sid = models.AutoField(primary_key=True)
    short_text = models.CharField(max_length=500, db_index=True)
    description = models.TextField()
    history = AuditLog()

    class Meta(object):
        db_table = 'solutions'

    def __str__(self):
        return self.short_text

    def __unicode__(self):
        return self.short_text

    def get_url(self):
        return '%s?pk=%s' % (reverse('view_all_solutions'), self.pk)


class UserProblems(models.Model):
    pid = models.AutoField(primary_key=True)
    short_text = models.CharField(max_length=500, db_index=True)
    description = models.TextField()
    history = AuditLog()

    class Meta(object):
        db_table = 'problems'

    def __str__(self):
        return self.short_text

    def __unicode__(self):
        return self.short_text

    def get_url(self):
        return '%s?pk=%s' % (reverse('view_call_problems'), self.pk)


class ProblemsAndSolutions(models.Model):
    id = models.AutoField(primary_key=True)
    solution = models.ForeignKey(Solutions, related_name='fk_problems_and_solutions_solution')
    problem = models.ForeignKey(UserProblems, related_name='fk_problems_and_solutions_problems')
    history = AuditLog()

    class Meta(object):
        db_table = 'problems_and_solutions'

    @staticmethod
    def get_url():
        return None


class CallHistory(models.Model):
    log_id = models.AutoField(primary_key=True)
    operator = models.ForeignKey(User, related_name='fk_call_history_operator_id')
    user = models.ForeignKey(User, related_name='fk_call_history_user_id')
    problem = models.ForeignKey(UserProblems, related_name='fk_call_history_problem_id')
    call_time = models.DateTimeField()
    solution = models.ForeignKey(Solutions, related_name='fk_call_support_solution_id')
    objects = OwnerManager()
    history = AuditLog()

    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username

    def get_url(self):
        return '%s?pk=%s' % (reverse('view_single_log'), self.pk)

    class Meta(object):
        db_table = 'call_support'
        permissions = (('view_call_history', 'View Call History'),)


class LockedUsers(models.Model):
    lid = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='fk_locked_users_user')
    lock_date = models.DateTimeField(db_index=True)
    ibs_locked = models.BooleanField(default=False, db_index=True)
    crm_locked = models.BooleanField(default=False, db_index=True)
    crm_comment = models.TextField()
    ibs_comment = models.TextField()
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'locked_users'
        permissions = (('unlock_crm_user', 'Unlock CRM Locked Account'),
                       ('unlock_ibs_user', 'Unlock IBS Locked Account'))

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?uid=%s' % (reverse('show user navigation menu'), self.user_id)


# V2
class VIPUsers(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='fk_vip_users_user')
    creator = models.ForeignKey(User, related_name='fk_vip_users_creator')
    is_deleted = models.BooleanField(default=False)
    delete_time = models.DateTimeField(null=True)
    create_time = models.DateTimeField(null=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'vip_users'
        permissions = (('view_vip_users', 'View list of vip users'),)

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?pk=%s' % (reverse('show user navigation menu'), self.pk)


class UserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True)
    gender = models.BooleanField(default=True)
    telephone = models.CharField(max_length=15, db_index=True)
    mobile = models.CharField(max_length=12, db_index=True)
    address = models.TextField()
    user = models.OneToOneField(User, related_name='fk_user_profile_user')
    birth_date = models.DateField(null=True)
    identity_number = models.CharField(max_length=15, db_index=True)
    geo_code = models.CharField(max_length=100, default='-')
    comment = models.TextField()
    marriage_date = models.DateField(null=True)
    marriage_date_day = models.IntegerField(null=True)
    marriage_date_month = models.IntegerField(null=True)
    birth_date_day = models.IntegerField(null=True)
    birth_date_month = models.IntegerField(null=True)
    is_dedicated = models.BooleanField(default=False, db_index=True)
    is_company = models.BooleanField(default=False, db_index=True)
    is_reseller = models.BooleanField(default=False, db_index=True)
    is_visitor = models.BooleanField(default=False, db_index=True)
    sh_number = models.CharField(default='', max_length=20)
    father_name = models.CharField(default='', max_length=100)
    # is_changed = models.BooleanField(default=False)
    # is_approved = models.BooleanField(default=False)
    validation_state = models.IntegerField(default=0)
    # 0 : Invalid
    # 1 : Change by User
    # 2 : Admin Accepted
    # 3 : Waiting For Accept
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'user_profile'
        permissions = (('view_profile', 'View User Profile'),
                       ('download_files', 'Download User Files'),
                       ('view_admins', 'View Admin Users'),
                       ('view_all_users', 'View All Users'),
                       ('view_personnel', 'View Personnel'),
                       ('view_normal_users', 'View Customers'),
                       ('view_online_crm_users', 'View Online CRM Users'),
                       ('add_new_users', 'Add New Users to CRM'),
                       ('search_users', 'Ability to Search Users'),
                       ('activate_internet_user', 'Activate Internet User'),
                       ('switch_account', 'Can Switch Accounts'),
                       ('switch_to_admin', 'Can Switch To Admin Users'),
                       ('switch_to_staff', 'Can Switch To Staff Users')
                       )

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?uid=%s' % (reverse('show user navigation menu'), self.user_id)


class NotifySettings(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    mail_text = models.TextField()
    sms_text = models.TextField()
    inbox_text = models.TextField()
    email_enabled = models.BooleanField(default=False)
    sms_enabled = models.BooleanField(default=False)
    inbox_enabled = models.BooleanField(default=False)
    code_id = models.IntegerField(default=0, db_index=True)
    description = models.TextField()
    history = AuditLog()

    class Meta(object):
        db_table = 'notify_settings'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('notify_config'), self.pk)


# V2
class ServiceGroups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'service_groups'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('service_group_management'), self.pk)


# V2
class UserServiceGroup(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='fk_user_service_group_user')
    service_group = models.ForeignKey(ServiceGroups, related_name='fk_user_user_service_group_service_group')
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'user_service_group'

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?uid=%s' % (reverse('show user navigation menu'), self.user_id)


# V2
class ServiceGroup(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(IBSService, related_name='fk_service_group_service')
    group = models.ForeignKey(ServiceGroups, related_name='fk_service_group_group')
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'service_group'

    def __str__(self):
        return self.service.name

    def __unicode__(self):
        return self.service.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('show all services'), self.service_id)


# V2
class PackageGroups(models.Model):
    id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Traffic, related_name='fk_package_groups_package')
    group = models.ForeignKey(ServiceGroups, related_name='fk_package_groups_group')
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'package_groups'

    def __str__(self):
        return self.package.name

    def __unicode__(self):
        return self.package.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('assign_package_to_group'), self.pk)


# V2
class ServiceGroupRouting(models.Model):
    id = models.AutoField(primary_key=True)
    group = models.ForeignKey(ServiceGroups, related_name='fk_service_group_routing_group')
    bank = models.IntegerField(default=1, db_index=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'service_group_routing'

    def __str__(self):
        return self.group.name

    def __unicode__(self):
        return self.group.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('group_routing_management'), self.pk)


# V2
class Banks(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=2550)
    internal_value = models.IntegerField(db_index=True)
    install_date = models.DateTimeField(auto_now=True, auto_created=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'banks0'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_url():
        return None


# V2
class BankProperties(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    value = models.TextField(default='')
    bank = models.ForeignKey(Banks, related_name='fk_bank_properties_bank')
    history = AuditLog()

    class Meta(object):
        db_table = 'banks_properties'

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('bank_api_data_management'), self.pk)


# V2
class UserCurrentService(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(IBSService, related_name='fk_user_current_service_service')
    user = models.ForeignKey(User, related_name='fk_user_current_service_user')
    is_active = models.BooleanField(default=False)
    expire_date = models.DateTimeField(default=None, blank=True, null=True)
    service_property = models.ForeignKey(ServiceProperty,
                                         related_name='fk_user_current_service_service_property',
                                         null=True)
    is_float = models.BooleanField(default=False, db_index=True)
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'user_current_service'
        permissions = (('update_service_from_ibs', 'Update User Service From IBSng'),
                       ('expire_user_service', 'Expire User Services'))

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?pk=%s' % (reverse('show user navigation menu'), self.user_id)


# V2
class IBSServiceDiscount(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    extended_days = models.IntegerField(db_index=True)
    price_discount = models.IntegerField()
    service = models.ForeignKey(ServiceProperty, related_name='fk_ibs_service_discount_service', null=True)
    is_deleted = models.BooleanField(default=False)
    charge_days = models.IntegerField(default=10, db_index=True)
    extra_traffic = models.IntegerField(default=0)
    history = AuditLog()

    class Meta(object):
        db_table = 'discounts'
        permissions = (('view_discount', 'View All Discounts'),)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('view_all_discount'), self.pk)


# v2.1 : moved here because of invoice table!
class IPPool(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=20, db_index=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    def __str__(self):
        return self.ip

    def __unicode__(self):
        return self.ip

    @staticmethod
    def get_url():
        return reverse('view_ip_statics')

    class Meta(object):
        db_table = 'ip_pool'

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


# v2.3
class InvoiceService(models.Model):
    id = models.AutoField(primary_key=True)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey()
    service_type = models.IntegerField(default=0)
    expire_date = models.DateTimeField(null=True)

    class Meta(object):
        db_table = 'invoice_service'


# v2.3
class InvoiceDiscount(models.Model):
    id = models.AutoField(primary_key=True)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey()

    class Meta(object):
        db_table = 'invoice_discount'


# V2
# New Changes : Added Multi Service Support in V 2.3!
class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True, null=True)
    price = models.IntegerField(default=0, db_index=True)
    user = models.ForeignKey(User, related_name='fk_invoice_user')
    service = models.ForeignKey(InvoiceService, related_name='fk_invoice_service')
    service_text = models.CharField(max_length=255)
    pay_time = models.DateTimeField(null=True, blank=True, db_index=True)
    ref_number = models.CharField(max_length=200, blank=True, db_index=True)
    is_paid = models.BooleanField(default=False, db_index=True)
    comment = models.TextField()
    create_time = models.DateTimeField(null=False, db_index=True)
    is_deleted = models.BooleanField(default=False)
    paid_online = models.BooleanField(default=False, db_index=True)
    extra_data = models.IntegerField(default=0)
    service_discount = models.ForeignKey(InvoiceDiscount, related_name='fk_invoice_discount_service', null=True)
    debit_price = models.IntegerField(default=0)
    dynamic_discount = models.IntegerField(default=0)
    price_round_down = models.IntegerField(default=0)
    tax = models.IntegerField(default=0)
    is_personnel_payment = models.BooleanField(default=False)
    is_system_payment = models.BooleanField(default=False)

    objects = CRMManager()
    history = AuditLog()

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?pk=%s' % (reverse('show all factors'), self.pk)

    class Meta(object):
        db_table = 'invoice_23'
        permissions = (('admin_payment', 'Free Invoice Payment'),
                       ('e_payment', 'Activate EPayment'),
                       ('buy_service', 'Buy Service'),
                       ('view_invoices', 'View All Invoices'),
                       ('print_invoice', 'Can Print Invoices'),
                       ('buy_package', 'Buy Traffic Package'),
                       ('view_complete_finance', 'View Analysis Financial'),
                       ('view_single_invoice', 'View Single Invoice'),
                       ('download_invoice_excel', 'Can Download Excel Report')
                       )


# V2
class InvoicePaymentTracking(models.Model):
    id = models.AutoField(primary_key=True)
    invoice = models.ForeignKey(Invoice, related_name='fk_invoice_payment_tracking_invoice')
    initial_res = models.TextField(null=True)
    final_res = models.TextField(null=True)
    start_time = models.DateTimeField(db_index=True)
    end_time = models.DateTimeField(db_index=True)
    is_success = models.BooleanField(default=False)
    history = AuditLog()

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)

    @staticmethod
    def get_url():
        return None

    class Meta(object):
        db_table = 'invoice_payment_tracking'


# v2.1
class VIPGroups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    group = models.ForeignKey(ServiceGroups, related_name='fk_vip_group_group')
    history = AuditLog()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('view_vip_groups'), self.pk)

    class Meta(object):
        db_table = 'vip_group'
        permissions = (('view_vip_group', 'View VIP Group'),)


# v2.1
class VIPServices(models.Model):
    id = models.AutoField(primary_key=True)
    service = models.ForeignKey(ServiceProperty, related_name='fk_vip_services_service')
    group = models.ForeignKey(VIPGroups, related_name='fk_vip_services_group')
    history = AuditLog()

    def __str__(self):
        return self.group.name

    def __unicode__(self):
        return self.group.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('show all services'), self.service_id)

    class Meta(object):
        db_table = 'vip_service'
        permissions = ()


# v2.1
class VIPUsersGroup(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='fk_vip_users_group_user')
    vip_group = models.ForeignKey(VIPGroups, related_name='fk_vip_users_group_vip_group')
    objects = OwnerManager()
    history = AuditLog()

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?pk=%s' % (reverse('show user navigation menu'), self.user_id)

    class Meta(object):
        db_table = 'vip_user_groups'


# v2.1
class VIPPackages(models.Model):
    id = models.AutoField(primary_key=True)
    package = models.ForeignKey(Traffic, related_name='fk_vip_packages_package')
    group = models.ForeignKey(VIPGroups, related_name='fk_vip_packages_group')
    history = AuditLog()

    def __str__(self):
        return self.package.name

    def __unicode__(self):
        return self.package.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('view all traffics'), self.package_id)

    class Meta(object):
        db_table = 'vip_package'
        permissions = ()


# v2.2.1    Moved Here because of dashboard
class DashboardTarget(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey()

    class Meta(object):
        db_table = 'dashboard_target_beta'


# v2.1
class Dashboard(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.TextField()
    # priority = models.IntegerField(default=2)
    create_date = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=255, db_index=True)
    is_read = models.BooleanField(default=False, db_index=True)
    is_done = models.BooleanField(default=False, db_index=True)
    done_date = models.DateTimeField(null=True, db_index=True)
    reader = models.ForeignKey(User, related_name='fk_dashboard_reader', null=True)
    sender = models.ForeignKey(User, related_name='fk_dashboard_sender')
    target_user = models.ForeignKey(User, related_name='fk_dashboard_target_user', null=True)
    # v2.2.1 : Added target to cover all the events on the system
    target = models.ForeignKey(DashboardTarget, related_name='fk_dashboard_target_target')
    group = models.ForeignKey(Group, related_name='fk_dashboard_group')
    # v2.2.1 : Added state to find the last state of the job
    last_state = models.IntegerField(default=0, db_index=True)
    target_text = models.TextField(default='--')
    history = AuditLog()

    def get_user(self):
        return self.target_user

    user = property(get_user)
    objects = OwnerManager()

    class Meta(object):
        db_table = 'dashboards'
        permissions = (('view_all_dashboards', 'View Dashboard for All Users'),
                       ('set_task_done', 'Set Task as Done'),
                       ('reference_to_others', 'Reference Task to Others'),
                       ('view_dashboard', 'View Group Dashboard'),
                       ('start_jobs', 'Start Doing a Job'),
                       ('view_job_summery', 'View Job Summery'),
                       ('report_before_start', 'Add Report Before Start Job'),
                       ('restart_job', 'Can Restart A Job'),
                       ('dash_excel_report', 'Download Dashboard Excel Report'),
                       ('upload_workbench_document', 'Upload Reports'),
                       ('download_workbench_reports', 'Download Reports'),
                       )


# v2.2.2
class DashboardCurrentGroup(models.Model):
    id = models.AutoField(primary_key=True)
    dashboard = models.ForeignKey(Dashboard, related_name='fk_dashboard_current_group_dashboard')
    group = models.ForeignKey(Group, related_name='fk_dashboard_current_group_group')
    history = AuditLog()

    class Meta(object):
        db_table = 'dashboard_current_group_222'

    @staticmethod
    def get_url():
        return None

    def __str__(self):
        return self.group.name

    def __unicode__(self):
        return self.group.name


# v2.1
class UserWorkHistory(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True, null=True)
    dashboard = models.ForeignKey(Dashboard, related_name='fk_user_work_history_dashboard')
    user = models.ForeignKey(User, related_name='fk_user_work_history_user')
    start_date = models.DateTimeField()
    group = models.ForeignKey(Group, related_name='fk_user_work_history_group')
    state = models.IntegerField(default=0)
    message = models.TextField()
    history = AuditLog()

    class Meta(object):
        db_table = 'user_work_histories1'
        permissions = (('view_work_history', 'View Work History'),
                       ('cancel_job', 'Cancel Started Job'))


# v2.1
class DashboardReferences(models.Model):
    id = models.AutoField(primary_key=True)
    reason = models.TextField(default='')
    user = models.ForeignKey(User, related_name='fk_dashboard_reference_user')
    dashboard = models.ForeignKey(Dashboard, related_name='fk_dashboard_reference_dashboard')
    target_group = models.ForeignKey(Group, related_name='fk_dashboard_reference_target_group')
    source_group = models.ForeignKey(Group, related_name='fk_dashboard_reference_source_group')
    ref_date = models.DateTimeField(auto_now=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'dashboard_rfc'
        ordering = ['-ref_date']


# v2.1
class DashboardRouting(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=36, default=None, db_index=True)
    message = models.CharField(max_length=255)
    group = models.ForeignKey(Group, related_name='fk_dashboard_routing_group')

    class Meta(object):
        db_table = 'dashboard_routes'
        permissions = (('view_dashboard_routing', 'View Dashboard Routing'),)


# v2.1
class UserIPStatic(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.ForeignKey(IPPool, related_name='fk_user_ip_static_ip', null=True)
    user = models.ForeignKey(User, related_name='fk_user_ip_static_user')
    is_reserved = models.BooleanField(default=False)
    expire_date = models.DateTimeField(null=True, db_index=True)
    release_date = models.DateTimeField(null=True, db_index=True)
    is_free = models.BooleanField(default=False, db_index=True)
    service_period = models.IntegerField(default=1, db_index=True)
    request_time = models.DateTimeField(null=True, db_index=True)
    start_date = models.DateTimeField(null=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?uid=%s' % (reverse('show user navigation menu'), self.user_id)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    class Meta(object):
        db_table = 'users_ip_static'
        permissions = (('buy_ip_static', 'Buy IP Static'),
                       ('assign_free_ip', 'Assign Free IP Address'),
                       ('view_ip_request', 'View Static IP Request'),
                       ('accept_ip_request', 'Accept IP Request'))
        # ordering = ['-expire_date']


class UserIPStaticHistory(models.Model):
    id = models.AutoField(primary_key=True)
    text_ip = models.CharField(max_length=25, default='-')
    last_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='fk_user_ip_static_history_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'user_ip_static_history'


# v2.1
class UserOwner(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now=True, db_index=True)
    user = models.OneToOneField(User, related_name='fk_user_owner_user')
    owner = models.ForeignKey(User, related_name='fk_user_owner_owner')
    history = AuditLog()

    class Meta(object):
        db_table = 'user_owner'


# V2.2
class Polls(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150, db_index=True)
    description = models.TextField()
    start_date = models.DateTimeField(null=True, db_index=True)
    end_date = models.DateTimeField(null=True, db_index=True)
    target_address = models.CharField(max_length=300)
    is_closed = models.BooleanField(default=False, db_index=True)
    is_deleted = models.BooleanField(default=False)
    extra_package = models.IntegerField(default=0)
    extra_days = models.IntegerField(default=0)
    history = AuditLog()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('poll_view'), self.pk)

    class Meta(object):
        db_table = 'polls22'
        permissions = (('configure_polls', 'Can Configure Polls'),
                       ('view_polls', 'Can View Polls')
                       )


# v2.2
class UserPolls(models.Model):
    id = models.AutoField(primary_key=True)
    completion_date = models.DateTimeField(null=True, db_index=True)
    poll = models.ForeignKey(Polls, related_name='fk_user_polls_poll')
    user = models.ForeignKey(User, related_name='fk_user_polls_user')
    is_finished = models.BooleanField(default=False, db_index=True)
    user_token = models.CharField(max_length=30, db_index=True)
    objects = OwnerManager()
    history = AuditLog()

    def __str__(self):
        return self.poll.name

    def __unicode__(self):
        return self.poll.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('poll_view'), self.poll_id)

    class Meta(object):
        db_table = 'user_poll22'
        permissions = (('vote_poll', 'Can vote for a poll'),)


# v 2.2.1
class DebitSubject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.CharField(max_length=500)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse(''), self.pk)

    class Meta(object):
        db_table = 'debit_subject_222'
        permissions = (('view_debit_subject', 'View Debit Subject'),)


# v2.2
class UserDebit(models.Model):
    id = models.AutoField(primary_key=True)
    amount = models.IntegerField(default=0, db_index=True)
    description = models.CharField(max_length=500)
    last_amount = models.IntegerField(default=0)
    last_update = models.DateTimeField(auto_now=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    subject = models.ForeignKey(DebitSubject, related_name='fk_user_debit_subject')
    user = models.ForeignKey(User, related_name='fk_user_debit_user')
    objects = OwnerManager()
    history = AuditLog()

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?pk=%s' % (reverse('debit_view'), self.pk)

    def save_for_onvoice(self, invoice):
        h = UserDebitHistory()
        h.new_comment = self.description
        h.old_value = self.last_amount
        h.new_value = self.amount
        h.user = self.user
        h.subject_name = self.subject.name
        h.invoice_id = invoice
        h.save()
        super(UserDebit, self).save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        h = UserDebitHistory()
        h.new_comment = self.description
        h.old_value = self.last_amount
        h.new_value = self.amount
        h.user = self.user
        h.subject_name = self.subject.name
        h.invoice = None
        h.save()
        super(UserDebit, self).save(force_insert, force_update, using, update_fields)

    class Meta(object):
        db_table = 'user_debit'
        permissions = (('view_user_debit', 'View User Debit'),
                       ('reset_user_debit', 'Reset User Debits'))


# v 2.2
class UserDebitHistory(models.Model):
    id = models.AutoField(primary_key=True)
    old_value = models.IntegerField(db_index=True)
    new_value = models.IntegerField(db_index=True)
    new_comment = models.CharField(max_length=500)
    subject_name = models.CharField(max_length=200, db_index=True)
    update_time = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, related_name='fk_user_debit_history_user')
    invoice = models.ForeignKey(Invoice, related_name='invoice_debit', null=True)
    objects = OwnerManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'user_debit_history_22'
        permissions = (('view_debit_history', 'Can View History'),)


# v2.2
class TelegramUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, db_index=True)
    user = models.ForeignKey(User, related_name='fk_telegram_user_user')
    register_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    objects = OwnerManager()
    history = AuditLog()

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?u=%s' % (reverse('telegram_view_users'), self.user_id)

    class Meta(object):
        db_table = 'telegram_user_22'
        permissions = (('view_telegram_user', 'Can View Telegram User'),
                       ('view_all_telegram_users', 'Can View All Telegram Users'))


# v2.2
class TelegramHistory(models.Model):
    id = models.AutoField(primary_key=True)
    message = models.CharField(max_length=4096)
    response = models.CharField(max_length=4096)
    send_date = models.DateTimeField(auto_now=True)
    telegram_user = models.ForeignKey(TelegramUser, related_name='fk_telegram_history_telegram_user')
    history = AuditLog()

    def __str__(self):
        return self.message

    def __unicode__(self):
        return self.message

    def get_url(self):
        return '%s?pk=%s' % (reverse('telegram_view_users'), self.pk)

    class Meta(object):
        db_table = 'telegram_history'
        permissions = (('view_telegram_history', 'Can View Telegram History'),
                       ('view_telegram_history_all', 'Can View Telegram History For All'))


# v2.2.1
class Tower(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, db_index=True)
    description = models.CharField(max_length=500)
    address = models.TextField()
    ibs_name = models.CharField(max_length=255, null=True, db_index=True)
    ibs_id = models.IntegerField(null=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    max_bw = models.PositiveIntegerField(default=0)
    has_test = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('tower_view'), self.pk)

    class Meta(object):
        db_table = 'tower_beta2'
        permissions = (('view_tower', 'Can View Towers'),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


# v2.2.1
class TowerProblemReport(models.Model):
    id = models.AutoField(primary_key=True)
    report_date = models.DateTimeField(auto_now=True, db_index=True)
    description = models.TextField()
    user = models.ForeignKey(User, related_name='fk_tower_problem_report_user')
    tower = models.ForeignKey(Tower, related_name='fk_tower_problem_report_tower')
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    def __str__(self):
        return self.tower.name

    def __unicode__(self):
        return self.tower.name

    def get_url(self):
        return '%s?pk=%s' % (reverse('tower_view'), self.tower_id)

    class Meta(object):
        db_table = 'tower_problem_report_22'


# v2.2.1
class UserTower(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name='fk_user_tower_user')
    tower = models.ForeignKey(Tower, related_name='fk_user_tower_tower')
    # objects = CRMManager()
    history = AuditLog()

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    def get_url(self):
        return '%s?uid=%s' % (reverse('show user navigation menu'), self.user_id)

    class Meta(object):
        db_table = 'user_tower_22'
        permissions = (('view_user_tower', 'Can View User Tower'),)


# v2.2.1
class DedicatedUserService(models.Model):
    id = models.AutoField(primary_key=True)
    is_deleted = models.BooleanField(default=False)
    service = models.CharField(max_length=255)
    ip_pool = models.CharField(max_length=255)
    price = models.TextField(default='--')
    status = models.IntegerField(default=0)
    user = models.ForeignKey(User, related_name='fk_dedicated_user_user')
    objects = OwnerManager()
    history = AuditLog()

    def __str__(self):
        return self.service

    def __unicode__(self):
        return self.service

    def get_url(self):
        return '%s?uid=%s' % (reverse('show user navigation menu'), self.user_id)

    class Meta(object):
        db_table = 'dedicated_user_service_25'
        permissions = (('view_dedicated_user', 'Can View Dedicated Users'),
                       ('view_dedicated_service', 'Can View Dedicated User Service'),
                       ('undo_deleted_dedicate', 'Can Undo Deleted Dedicated User'))


# v2.2.1
class CompanyData(models.Model):
    id = models.AutoField(primary_key=True)
    zip_code = models.CharField(max_length=20)
    economic_code = models.CharField(max_length=100)
    identity_code = models.CharField(max_length=100, db_index=True)
    registration_number = models.CharField(max_length=100)
    user = models.OneToOneField(User, related_name='fk_company_data_user')
    objects = OwnerManager()
    history = AuditLog()

    def __str__(self):
        return self.user.username

    def __unicode__(self):
        return self.user.username

    @staticmethod
    def get_url():
        return None

    class Meta(object):
        db_table = 'company_data_user_22'
        permissions = (('view_company_data', 'Can View Company Data'),)


# v2.2.1
class ResellerProfile(models.Model):
    id = models.AutoField(primary_key=True)
    profit_price = models.FloatField(default=0)
    old_price = models.FloatField(default=0)
    last_update = models.DateTimeField(auto_now=True, db_index=True)
    user = models.OneToOneField(User, related_name='fk_reseller_profile_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'resellers_profile'
        permissions = (('view_resellers', 'Can View Reseller Users'),
                       ('access_reseller', 'Can Access Reseller Panel'),
                       ('edit_reseller_profit', 'Can Edit Reseller Profit'),
                       ('view_all_reseller_data', 'Can View All Reseller Data')
                       )

    def __str__(self):
        return self.user.first_name

    def __unicode__(self):
        return self.user.first_name

    def get_url(self):
        pass

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        rx = ResellerProfitHistory()
        rx.user_id = self.user_id
        rx.new_value = self.profit_price
        rx.old_value = self.old_price
        rx.save()
        super(ResellerProfile, self).save(force_insert, force_update, using, update_fields)


# v2.2.1 => This table is created to extend features! only 1 field is used at this time
class ResellerProfitOption(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    service_profit = models.IntegerField(default=0)
    package_profit = models.IntegerField(default=0)
    max_neg_credit = models.PositiveIntegerField(default=0)
    reseller = models.OneToOneField(ResellerProfile, related_name='fk_reseller_profit_option_reseller')
    history = AuditLog()

    class Meta(object):
        db_table = 'reseller_profit_options'

    def get_url(self):
        pass

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name


class PricePackage(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True)
    name = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'price_packages'
        permissions = (('view_price_package', 'View Price Package'),
                       ('buy_price_package', 'Can Buy Price Package'),
                       ('view_all_price_package', 'Can View All Packages to Buy'))

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        pass

    def remove(self):
        self.is_deleted = True
        self.save()


class PricePackageGroup(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True)
    group = models.ForeignKey(Group, related_name='fk_price_package_group_group')
    price_package = models.ForeignKey(PricePackage, related_name='fk_price_package_group_price_package')
    history = AuditLog()

    class Meta(object):
        db_table = 'price_package_groups'

    def __str__(self):
        return self.group.name

    def __unicode__(self):
        return self.group.name

    def get_url(self):
        pass


# v2.2.1
class ResellerProfitHistory(models.Model):
    id = models.AutoField(primary_key=True)
    new_value = models.FloatField(default=0)
    old_value = models.FloatField(default=0)
    update_date = models.DateTimeField(auto_now=True, db_index=True)
    user = models.ForeignKey(User, related_name='fk_reseller_profile_history_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'resellers_profile_history'


class CalendarEventType(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True, null=True)
    name = models.CharField(max_length=100, db_index=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'calendar_event_type_222'
        permissions = (('view_calendar_event_type', 'View Calendar Event Type'),)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    @staticmethod
    def get_url():
        return None

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class WorkingTime(models.Model):
    id = models.AutoField(primary_key=True)
    start_time = models.TimeField(null=True)
    end_time = models.TimeField(null=True)
    name = models.CharField(max_length=100)
    week_days = (('0', 0), ('1', 1), ('2', 2), ('3', 3), ('4', 4), ('5', 5), ('6', 6))
    week_day = models.IntegerField(choices=week_days, default=0)
    resource = models.IntegerField(default=1)
    event_type = models.ForeignKey(CalendarEventType, related_name='fk_working_time_event_type', null=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'working_time_222'
        permissions = (('fill_working_time', 'Fill Working Time For Users'),
                       ('view_working_time', 'View Working Time')
                       )

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name


class Calendar(models.Model):
    id = models.AutoField(primary_key=True)
    cal_month = models.IntegerField(null=True, db_index=True)
    cal_year = models.IntegerField(null=True, db_index=True)
    cal_day = models.IntegerField(null=True, db_index=True)
    priority = models.IntegerField(default=1)
    work_time = models.ForeignKey(WorkingTime, related_name='fk_calendar_working_time')
    dashboard = models.ForeignKey(Dashboard, related_name='fk_calendar_dashboard')
    # event_type = models.ForeignKey(CalendarEventType, related_name='fk_calendar_event_type')
    history = AuditLog()

    class Meta(object):
        db_table = 'calendar_222'
        permissions = (('view_calendar', 'View Calendar'),
                       )

    def __str__(self):
        return str(self.pk)

    def __unicode__(self):
        return str(self.pk)

    @staticmethod
    def get_url():
        return '%s' % reverse('calendar_view_all')


# v2.3
class TransportType(models.Model):
    id = models.AutoField(primary_key=True)
    external = AutoUUIDField(db_index=True)
    last_update = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, db_index=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'transport_type_23'
        permissions = (('view_transport_type', 'View Transport Type'), )

    def get_url(self):
        return '%s?searchPhrase=%s' % (reverse('transport_view_types'), self.name)

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name

    def get_ext(self):
        return self.external

    ext = property(get_ext)


# v 2.3
class Transportation(models.Model):
    id = models.AutoField(primary_key=True)
    external = AutoUUIDField(db_index=True)
    last_update = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.CharField(max_length=500)
    is_deleted = models.BooleanField(default=False)
    transport_type = models.ForeignKey(TransportType, related_name='fk_transportation_transport_type')
    history = AuditLog()

    class Meta(object):
        db_table = 'transportation_23'
        permissions = (('view_transportation', 'View Transportation'),)

    def get_url(self):
        return '%s?pk=%s' % (reverse('transport_view'), self.pk)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_ext(self):
        return self.external

    ext = property(get_ext)


class TicketTransportation(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_column='external')
    add_time = models.DateTimeField(auto_now=True, db_index=True)
    dashboard = models.ForeignKey(Dashboard, related_name='fk_ticket_transportation_dashboard', db_index=True)
    transport = models.ForeignKey(Transportation, related_name='fk_ticket_transportation_transport')
    history = AuditLog()

    class Meta(object):
        db_table = 'ticket_transportation_23'


class TicketTeam(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_column='external', db_index=True)
    add_time = models.DateTimeField(auto_now=True)
    dashboard = models.ForeignKey(Dashboard, related_name='fk_ticket_team_dashboard', db_index=True)
    user = models.ForeignKey(User, related_name='fk_ticket_team_user', db_index=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'ticket_team_224'
        permissions = (('add_ticket_partner', 'Add Partner to Ticket'),)

    def __str__(self):
        return self.user.first_name

    def __unicode__(self):
        return self.user.first_name

    @staticmethod
    def get_url():
        return None


class PopSite(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_column='external', db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.CharField(max_length=500, default='-')
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'pop_site'
        permissions = (('view_pop_site', 'Can View Pop Sites'),)

    def get_url(self):
        pass

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def remove(self):
        self.is_deleted = True
        self.save()


class EquipmentType(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_type'
        permissions = (('view_equipment_type', 'Can view equipment type'),)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        pass

    def remove(self):
        self.is_deleted = True
        self.save()


class EquipmentCode(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    code = models.CharField(max_length=100, db_index=True)
    sell_price = models.PositiveIntegerField(default=0)
    used_sell_price = models.PositiveIntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_code'
        permissions = (('view_equipment_code', 'Can View Equipment Code'),)

    def __str__(self):
        return str(self.code)

    def __unicode__(self):
        return str(self.code)

    def get_url(self):
        pass

    def remove(self):
        self.is_deleted = True
        self.save()


class EquipmentGroup(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.CharField(max_length=500)
    is_deleted = models.BooleanField(default=False)
    remain_items = models.IntegerField(default=0)
    used_remain_items = models.IntegerField(default=0)
    code = models.ForeignKey(EquipmentCode, related_name='fk_equipment_group_code')
    equipment_type = models.ForeignKey(EquipmentType, related_name='fk_equipment_group_equipment_type')
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'equipment_group'
        permissions = (('view_equipment_group', 'Can View Equipment Group'),)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        pass

    def remove(self):
        self.is_deleted = True
        self.save()

    def change_remain(self, plus_used=1, plus_original=0):
        self.used_remain_items += plus_used
        self.remain_items += plus_original
        self.save()


class Equipment(models.Model):
    id = models.AutoField(primary_key=True, db_index=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    description = models.CharField(max_length=500)
    serial = models.CharField(max_length=150, db_index=True)
    is_used = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_involved = models.BooleanField(default=False)
    last_update = models.DateTimeField(auto_now=True)
    group = models.ForeignKey(EquipmentGroup, related_name='fk_equipment_group', db_index=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment'
        permissions = (('view_equipment', 'Can View Equipment'),
                       ('view_equipment_history', 'View Equipment History'))

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        pass

    def remove(self):
        self.is_deleted = True
        if self.is_used:
            self.group.change_remain()
        else:
            self.group.change_remain(0, 1)
        self.save()


class EquipmentStateList(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=200, db_index=True)
    description = models.CharField(max_length=500)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_state_list'
        permissions = (('view_equipment_state_list', 'Can View Equipment State List'),)

    def __str__(self):
        return self.name

    def __unicode__(self):
        return self.name

    def get_url(self):
        pass

    def remove(self):
        self.is_deleted = True
        self.save()


class EquipmentState(models.Model):
    id = models.AutoField(primary_key=True)
    last_update = models.DateTimeField(auto_now=True, db_index=True)
    equipment = models.ForeignKey(Equipment, related_name='fk_equipment_state_equipment')
    state = models.ForeignKey(EquipmentStateList, related_name='fk_equipment_state_state')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_state'

    def __unicode__(self):
        return self.equipment.name

    def __str__(self):
        return self.equipment.name

    def get_url(self):
        pass

    def delete(self, using=None):   # Prevent Delete
        pass

    def remove(self):   # Prevent Delete
        pass


class EquipmentOrderType(models.Model):
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey()
    # item_text = models.CharField(max_length=255)

    class Meta(object):
        db_table = 'equipment_order_type'


class EquipmentOrder(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    item_text = models.CharField(max_length=255, db_index=True)
    request_date = models.DateTimeField(db_index=True)
    receive_date = models.DateTimeField(null=True, db_index=True)
    is_processing = models.BooleanField(default=False)
    is_borrow = models.BooleanField(default=False, db_index=True)
    personnel = models.ForeignKey(User, related_name='fk_equipment_order_personnel', db_index=True)
    order_type = models.ForeignKey(EquipmentOrderType, related_name='fk_equipment_order_order_type', db_index=True)
    receiver = models.ForeignKey(User, related_name='fk_equipment_order_receiver', null=True, db_index=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_order'
        permissions = (('view_all_orders', 'View all personnel order'),
                       ('view_order_details', 'View Order Details'),
                       ('commit_delivery', 'Commit Order Delivery'))

    def __str__(self):
        return self.item_text

    def __unicode__(self):
        return self.item_text

    def get_url(self):
        return '%s?oi=%s' % (reverse('equipment_order_view'), self.pk)

    def item_is_processing(self):
        self.is_processing = True
        self.save()

    def start_job(self):
        self.is_processing = True
        self.save()

    def delete(self, using=None):
        pass

    def remove(self):
        self.item_rejected()


class EquipmentInUse(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    last_update = models.DateTimeField(auto_now=True)
    order_type = models.ForeignKey(EquipmentOrderType, related_name='fk_equipment_iin_use_order_type')
    order = models.ForeignKey(EquipmentOrder, related_name='fk_equipment_in_use_order')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_in_user'


class EquipmentUnknownCondition(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField()
    add_date = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(EquipmentOrder, related_name='fk_equipment_unknown_condition_order')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_unknown_condition'

    def get_url(self):
        pass

    def __str__(self):
        return self.order.item_text

    def __unicode__(self):
        return self.order.item_text


class EquipmentOrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True)
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    change_date = models.DateTimeField(auto_now=True)
    reason = models.CharField(max_length=500, default='-')
    is_used = models.BooleanField(default=False)
    equipment = models.ForeignKey(EquipmentGroup, related_name='fk_equipment_order_item_equipment', db_index=True)
    order = models.ForeignKey(EquipmentOrder, related_name='fk_equipment_order_item_order', db_index=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'equipment_order_item'

    def accept(self):
        self.is_accepted = True
        self.is_rejected = False
        self.reason = '-'
        self.save()

    def reject(self, reason):
        self.is_accepted = False
        self.is_rejected = True
        self.reason = reason
        self.save()
        if self.is_used:
            self.equipment.change_remain()
        else:
            self.equipment.change_remain(0, 1)

    def __str__(self):
        return self.equipment.name

    def __unicode__(self):
        return self.equipment.name

    def get_url(self):
        pass

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class EquipmentOrderDetail(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    change_date = models.DateTimeField(auto_now=True)
    equipment = models.ForeignKey(Equipment, related_name='fk_equipment_order_detail_equipment')
    order_item = models.ForeignKey(EquipmentOrderItem, related_name='fk_equipment_order_detail_order_item')
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_order_detail'

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class EquipmentBorrow(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_column='external', unique=True)
    address = models.CharField(max_length=500)
    property_number = models.CharField(max_length=500, db_index=True)
    last_update = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(EquipmentOrderDetail, related_name='fk_equipment_borrow_order')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_borrow'

    def __str__(self):
        return self.address

    def __unicode__(self):
        return self.address

    def get_url(self):
        pass


class EquipmentReturn(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    return_date = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(EquipmentOrderDetail, related_name='fk_equipment_return_order_item')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_return'

    def __str__(self):
        return self.order.equipment.group.name

    def __unicode__(self):
        return self.order.equipment.group.name

    def get_url(self):
        pass


class EquipmentExit(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    exit_date = models.DateTimeField(auto_now=True)
    order = models.ForeignKey(EquipmentOrderDetail, related_name='fk_equipment_exit_order_item')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_exit'

    def __str__(self):
        return self.order.equipment.group.name

    def __unicode__(self):
        return self.order.equipment.group.name

    def get_url(self):
        pass


class InvolvedEquipment(models.Model):
    """
    Define where the hell is this using? User, Tower or Pop Sites?
    """
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    item_text = models.CharField(max_length=255, db_index=True)
    order = models.ForeignKey(EquipmentOrder, related_name='fk_involved_equipment_order')
    equipment = models.ForeignKey(Equipment, related_name='fk_involved_equipment_equipment')
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'involved_equipment'

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def remove(self):
        self.is_deleted = True
        self.save()


class EquipmentInstalled(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    install_date = models.DateTimeField()
    is_installed = models.BooleanField(default=False, db_index=True)
    checkout_done = models.BooleanField(default=False, db_index=True)
    checkout_date = models.DateTimeField(null=True, db_index=True)
    comment = models.TextField(default='-')
    order_detail = models.OneToOneField(EquipmentOrderDetail, related_name='fk_equipment_installed_order_detail')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_installed'
        permissions = (('equipment_checkout', 'Can Checkout Equipment'),)


class EquipmentTempOrder(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    last_update = models.DateTimeField(auto_now=True)
    is_used = models.BooleanField(default=False)
    group = models.ForeignKey(EquipmentGroup, related_name='fk_equipment_temp_order')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_temp_order'


class EquipmentItemCountHistory(models.Model):
    id = models.AutoField(primary_key=True)
    change = models.FloatField(default=0)
    update_date = models.DateTimeField(auto_now=True)
    equipment = models.ForeignKey(Equipment, related_name='fk_equipment_item_count_history_equipment')
    history = AuditLog()

    class Meta(object):
        db_table = 'equipment_item_count_history'


class DocumentUploadType(models.Model):
    id = models.AutoField(primary_key=True)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey()
    upload_type = models.IntegerField()
    history = AuditLog()

    class Meta(object):
        db_table = 'document_upload_type'


class DocumentUpload(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    upload_date = models.DateTimeField(auto_now=True)
    file_name = models.CharField(max_length=200)
    original_name = models.CharField(max_length=200, db_index=True)
    upload_type_text = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    upload_type = models.ForeignKey(DocumentUploadType, related_name='fk_document_upload_upload_type')
    uploader = models.ForeignKey(User, related_name='fk_document_upload_uploader')
    user = models.ForeignKey(User, related_name='fk_document_upload_user')
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'document_upload'
        permissions = (('upload_file', 'Can Upload Files'),
                       ('view_uploaded_files', 'Can View uploaded files')
                       )


class LetterFile(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'letter_file'
        permissions = (('view_letter_file', 'Can View Letter File'),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class PocketBook(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'pocket_book'
        permissions = (('view_pocket_book', 'Can View Pocket Book'),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class IndicatorBook(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    code = models.CharField(max_length=255, db_index=True)
    create_date = models.DateTimeField(auto_now=True)
    send_date = models.DateField(db_index=True)
    target = models.CharField(max_length=255, db_index=True)
    title = models.CharField(max_length=1024, db_index=True)
    has_attachment = models.BooleanField(default=False)
    book_type = models.IntegerField(default=0)
    receive_date = models.DateField(null=True, db_index=True)
    # Extra field to check when user or target received the letter!
    related_person = models.CharField(max_length=255, null=True, db_index=True)
    is_deleted = models.BooleanField(default=False)
    letter_file = models.ForeignKey(LetterFile, related_name='fk_indicator_book_letter_file', null=True)
    pocket = models.ForeignKey(PocketBook, related_name='fk_indicator_book_pocket', null=True)
    user = models.ForeignKey(User, related_name='fk_indicator_book_user')
    objects = CRMManager()
    history = AuditLog()

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    class Meta(object):
        db_table = 'indicator_book'
        permissions = (('view_indicator', 'Can View Indicators Book'),)


class RelatedLetter(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    letter1 = models.ForeignKey(IndicatorBook, related_name='fk_related_letter_letter1')
    letter2 = models.ForeignKey(IndicatorBook, related_name='fk_related_letter_letter2')
    history = AuditLog()

    class Meta(object):
        db_table = 'related_letter'


class IndicatorObject(models.Model):
    id = models.AutoField(primary_key=True)
    object_id = models.PositiveIntegerField()
    content_type = models.ForeignKey(ContentType)
    content_object = GenericForeignKey()
    indicator = models.ForeignKey(IndicatorBook, related_name='fk_indicator_object_indicator')
    history = AuditLog()

    class Meta(object):
        db_table = 'indicator_object'


class DedicatedUserProfile(models.Model):
    id = models.AutoField(primary_key=True)
    contact = models.CharField(max_length=500)
    user = models.OneToOneField(User, related_name='fk_dedicated_user_profile_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_user_profile'
        permissions = (('edit_dedicated_profile', 'Can Edit Dedicated Profile'),)


class DedicatedInvoiceType(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_invoice_type'
        permissions = (('view_dedicated_invoice_type', "Can View Invoice Types"),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class SendType(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'send_type'


class DedicatedInvoice(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    price = models.FloatField(default=0)
    tax = models.IntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    system_invoice_number = models.PositiveIntegerField(default=0)
    description = models.CharField(max_length=500)
    send_date = models.DateTimeField(null=True)
    is_deleted = models.BooleanField(default=False)
    send_type = models.ForeignKey(SendType, related_name='fk_dedicated_invoice_send_type', null=True)
    invoice_type = models.ForeignKey(DedicatedInvoiceType, related_name='fk_dedicated_invoice_invoice_type')
    user = models.ForeignKey(User, related_name='fk_dedicated_invoice_user')
    creator = models.ForeignKey(User, related_name='fk_dedicated_invoice_creator')
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_invoices'
        permissions = (('view_dedicated_invoice', 'Can View Dedicated Invoices'),
                       ('checkout_invoice', 'Can Checkout Dedicate Invoice'),
                       ('change_invoice_state', 'Can Change Invoice State'),
                       ('update_send_type', 'Can Update Send Type'))

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.pk and (self.send_type_id is None and self.send_type is not None) or \
                (self.send_type_id is not None and self.send_type is None) or (self.send_type_id and self.send_type):
            dx = DedicatedInvoiceSendHistory()
            dx.invoice_id = self.pk
            if self.send_type_id:
                dx.send_type_id = self.send_type_id
            else:
                dx.send_type_id = self.send_type.pk
            dx.user_id = self.creator_id
            dx.save()
        super(DedicatedInvoice, self).save(force_insert, force_update, using, update_fields)

    def __unicode__(self):
        return self.user.first_name


class DedicatedInvoiceSendHistory(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    change_date = models.DateTimeField(auto_now=True)
    receiver = models.CharField(max_length=255, null=True)
    send_type = models.ForeignKey(SendType, related_name='fk_dedicated_invoice_send_history_send_type')
    user = models.ForeignKey(User, related_name='fk_dedicated_invoice_send_history_user')
    invoice = models.ForeignKey(DedicatedInvoice, related_name='fk_dedicated_invoice_send_history_invoice')
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_invoice_history'


class DedicatedInvoiceState(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.IntegerField(default=0, db_index=True)
    next_change = models.DateTimeField(null=True)
    invoice = models.OneToOneField(DedicatedInvoice, related_name='fk_dedicated_invoice_state_invoice')
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_invoice_state'


class DedicatedInvoiceStateHistory(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.IntegerField(default=0, db_index=True)
    update_time = models.DateTimeField(auto_now=True)
    extra_data = models.CharField(max_length=500)
    user = models.ForeignKey(User, related_name='fk_dedicated_invoice_state_history_user')
    invoice = models.ForeignKey(DedicatedInvoice, related_name='fk_dedicated_invoice_state_history_invoice')
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_invoice_state_history'


class UserMailConfig(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    username = models.CharField(max_length=100, db_index=True)
    password = models.CharField(max_length=100)
    user = models.OneToOneField(User, related_name='fk_user_mail_config_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'user_mail_config'
        permissions = (('access_mail_box', 'Can Use CRM Mail'),)


class MailMessage(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    message = models.TextField()
    html = models.TextField(null=True)
    subject = models.TextField(null=True)
    mail_date = models.DateTimeField()
    return_path = models.CharField(max_length=255)
    sender = models.CharField(max_length=255, db_index=True)
    to = models.CharField(max_length=255, db_index=True)
    mail_agent = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False, db_index=True)
    is_important = models.BooleanField(default=False, db_index=True)
    has_attachment = models.BooleanField(default=False)
    # next_number = models.BigIntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    sender_user = models.ForeignKey(User, related_name='fk_mail_message_sender_user', null=True)
    user = models.ForeignKey(User, related_name='fk_mail_message_user')

    class Meta(object):
        db_table = 'mail_message'
        permissions = (('access_mail_box', 'Can Access Mail Box'),
                       ('view_others_mail', 'Can Access All Mail Boxes'))
        ordering = ['-mail_date']


class IBSGroupCharge(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    ibs_name = models.CharField(max_length=255, db_index=True)
    ibs_id = models.IntegerField(db_index=True)
    description = models.CharField(max_length=500)
    history = AuditLog()

    class Meta(object):
        db_table = 'group_charge'


class IBSIpPool(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    comment = models.CharField(max_length=500)
    ibs_id = models.IntegerField(db_index=True)
    ibs_name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()

    class Meta(object):
        db_table = 'ibs_ip_pool'

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class ServiceFormula(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    formula = models.TextField(default="0")
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'service_formula'
        permissions = (('view_formula', 'Can View Formula'),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class BasicService(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    base_ratio = models.FloatField(default=0)
    service_index = models.IntegerField(default=1)
    is_deleted = models.BooleanField(default=False)
    max_bw = models.IntegerField(default=128)
    formula = models.ForeignKey(ServiceFormula, related_name='fk_basic_service_formula')
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'basic_service'
        permissions = (('view_basic_service', 'Can View Basic Services'),
                       ('import_ibs_groups', 'Can Import IBS Groups')
                       )

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class FloatDiscount(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    charge_month = models.IntegerField(db_index=True)
    extra_charge = models.IntegerField()
    extra_package = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'float-service_discount'
        permissions = (('view_float_discount', 'View Float Discounts'),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class ServiceAlias(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    service = models.ForeignKey(BasicService, related_name='fk_service_alias_basic_service')
    group = models.ForeignKey(IBSService, related_name='fk_service_alias_group')
    history = AuditLog()

    class Meta(object):
        db_table = 'service_alias'


# Determine if no ibs groups found in options so witch one should i choose
class BasicServiceDefaultGroup(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True)
    service = models.ForeignKey(BasicService, related_name='fk_basic_service_default_group_service')
    group = models.ForeignKey(IBSService, related_name='fk_basic_service_default_group_group')
    group_type = models.IntegerField(default=1)
    history = AuditLog()

    class Meta(object):
        db_table = 'basic_service_default_group'


class CustomOptionGroup(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    view_order = models.PositiveIntegerField()
    group_help = models.CharField(max_length=2000, default='-')
    is_required = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    can_recharge = models.BooleanField(default=False, db_index=True)
    metric = models.CharField(max_length=255, null=True)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'custom_option_group7'
        permissions = (('view_custom_option_group', 'Can View Option Groups'),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class CustomOption(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    min_value = models.FloatField(default=0)
    max_value = models.FloatField(default=0)
    var_name = models.CharField(max_length=10, db_index=True)
    is_custom_value = models.BooleanField(default=False, db_index=True)
    custom_value_min = models.PositiveIntegerField(default=0)
    custom_value_max = models.PositiveIntegerField(default=0)
    help_text = models.TextField(default='-')
    package = models.PositiveIntegerField(default=0)
    # service = models.ForeignKey(BasicService, related_name='fk_custom_option_service', null=True)
    group_type = models.IntegerField(default=0, db_index=True)
    pool = models.ForeignKey(IBSIpPool, related_name='fk_custom_option_pool', null=True)
    group = models.ForeignKey(CustomOptionGroup, related_name='fk_custom_option')
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'custom_option'
        permissions = (('view_custom_option', 'View Custom Options'),)

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class CustomOptionGroupMap(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    service = models.ForeignKey(BasicService, related_name='fk_custom_option_group_map_service')
    option = models.ForeignKey(CustomOption, related_name='fk_custom_option_group_map_option')
    group = models.ForeignKey(IBSService, related_name='fk_custom_option_group_map_group')
    history = AuditLog()

    class Meta(object):
        db_table = 'custom_option_group_map'


class ServiceOptions(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    service = models.ForeignKey(BasicService, related_name='fk_service_options_service')
    option = models.ForeignKey(CustomOption, related_name='fk_service_options_option')
    history = AuditLog()

    class Meta(object):
        db_table = 'service_options'


class CustomOptionRelateGroup(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    option = models.ForeignKey(CustomOption, related_name='fk_custom_option_related_group_option')
    group = models.ForeignKey(CustomOptionGroup, related_name='fk_custom_option_related_group_group')
    history = AuditLog()

    class Meta(object):
        db_table = 'custom_option_related_group'
        permissions = (('view_option_relation', 'Can View Option Relation'),)


class UserFloatTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    create_date = models.DateTimeField()
    is_system = models.BooleanField(default=True, db_index=True)
    is_public_test = models.BooleanField(default=False)
    is_test = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    final_price = models.PositiveIntegerField(default=0)
    service_period = models.IntegerField(default=1)
    service = models.ForeignKey(BasicService, related_name='fk_user_float_template_service')
    user = models.ForeignKey(User, related_name='fk_user_float_template_user')
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'user_float_template'
        permissions = (('view_user_template', 'Can View User Templates'),
                       ('view_all_templates', 'Can View All Users Template')
                       )

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


#  Options will inserted here and main template name and user identity will save on last model
class FloatTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    price = models.PositiveIntegerField(default=0)
    total_price = models.PositiveIntegerField(default=0)
    value = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    option = models.ForeignKey(CustomOption, related_name='fk_float_template_option')
    template = models.ForeignKey(UserFloatTemplate, related_name='fk_float_template_template')
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'float_template'


class UserActiveTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    user = models.ForeignKey(User, related_name='fk_user_active_template_user')
    template = models.ForeignKey(UserFloatTemplate, related_name='fk_user_active_template_template')
    history = AuditLog()

    class Meta(object):
        db_table = 'user_active_template'


class UserServiceState(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    value = models.IntegerField(default=0)
    purchase_date = models.DateTimeField()
    last_update = models.DateTimeField(auto_now=True)
    current_value = models.IntegerField(default=0)
    is_expired = models.BooleanField(default=False)
    charge_month = models.IntegerField(default=1)
    option = models.ForeignKey(CustomOption, related_name='fk_user_service_state_option')
    user = models.ForeignKey(User, related_name='fk_user_service_state_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'user_service_state'


class AssignedUserTemplate(models.Model):
    id = models.AutoField(primary_key=True, db_index=True, unique=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    user = models.ForeignKey(User, related_name='fk_assigned_user_template_user')
    template = models.ForeignKey(UserFloatTemplate, related_name='fk_assigned_user_template_template')
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'assigned_user_template'

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class AssignedTowerTemplate(models.Model):
    id = models.AutoField(primary_key=True, db_index=True, unique=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    tower = models.ForeignKey(Tower, related_name='fk_assigned_tower_template_tower')
    template = models.ForeignKey(UserFloatTemplate, related_name='fk_assigned_tower_template_template')
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'assigned_tower_template'

    def delete(self, using=None):
        self.is_deleted = True
        self.save()


class TempCharge(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    credit = models.IntegerField(default=0)
    days = models.IntegerField(default=0)
    report_date = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    charger = models.ForeignKey(User, related_name='fk_temp_charge_charger')    # personnel of may be self!
    user = models.ForeignKey(User, related_name='fk_temp_charge_user')   # IBS User
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'temp_charge'
        permissions = (('can_view_temp_charge', 'Can Use Temp Charge'),  # add to group to view menu
                       ('can_report_temp_recharge', 'Can Report Temp Charges'))  # view report


class TempChargeState(models.Model):
    """
    Indicate that how much user can buy temp charge!
    """
    id = models.AutoField(primary_key=True)
    credit = models.IntegerField(default=0)
    days = models.IntegerField(default=0)
    total_count = models.IntegerField(default=0)
    last_update = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    is_locked = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='fk_temp_charge_state_user')    # Service Owner
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'temp_charge_state'
        permissions = (('can_reset_temp', 'Can Reset Temp Charge'),)


# Temp Charge Invoice
class TempInvoice(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    credit = models.IntegerField(default=0)
    credit_price = models.IntegerField(default=0)
    days = models.IntegerField(default=0)
    days_price = models.IntegerField(default=0)
    is_deleted = models.BooleanField(default=False)
    user = models.ForeignKey(User, related_name='fk_temp_invoice_user')
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'temp_invoice'


class PreRegister(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    register_date = models.DateTimeField(auto_now=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    mobile = models.CharField(max_length=20, db_index=True)
    telephone = models.CharField(max_length=20, db_index=True)
    tower = models.CharField(max_length=255, null=True, db_index=True)
    region = models.CharField(max_length=255, null=True, db_index=True)
    is_man = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    is_started = models.BooleanField(default=False)
    personal = models.BooleanField(default=True)
    responsible = models.ForeignKey(User, related_name='fk_pre_register_responsible', null=True)
    history = AuditLog()

    class Meta(object):
        db_table = 'pre_registered'
        permissions = (("view_pre_register_user", 'View Users registered on web'),
                       )

    def start_job(self):
        self.is_started = True
        self.save()

    def assign_job(self, user):
        self.responsible = user
        self.save()


class InvoiceChargeState(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    success = models.BooleanField(default=False, db_index=True)
    last_update = models.DateTimeField(auto_now=True)
    failed_action = models.CharField(max_length=500)
    reason = models.CharField(max_length=100)
    is_resolved = models.BooleanField(default=False, db_index=True)
    invoice = models.ForeignKey(Invoice, related_name='fk_invoice_charge_state_invoice')
    history = AuditLog()

    class Meta(object):
        db_table = 'invoice_charge_state'
        permissions = (('view_invoice_charge', 'Can View Invoice Charge State'),
                       )


class Leader(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'leader'


class VisitorProfile(models.Model):
    PAYMENT_TYPES = ((0, 'one time'), (1, 'periodic payment'))
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    deposit = models.PositiveIntegerField(default=0, db_index=True)
    last_payment = models.DateTimeField(null=True, db_index=True)
    payment_type = models.IntegerField(default=0, choices=PAYMENT_TYPES, db_index=True)
    user = models.OneToOneField(User, related_name='fk_visitor_profile_user_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'visitor_profile'
        permissions = (('view_visitors', 'Can View Visitors'), ('view_visitor_profile', 'Can View Visitor Profile'),
                       ('visitor_checkout', 'Can Checkout Visitor')
                       )


class UserCreator(models.Model):
    id = models.AutoField(primary_key=True)
    create_date = models.DateTimeField(auto_now=True)
    creator = models.ForeignKey(User, related_name='fk_user_creator_creator')
    user = models.OneToOneField(User, related_name='fk_user_creator_user')
    history = AuditLog()

    class Meta(object):
        db_table = 'user_creator'


class OneTimePayment(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    is_checkout = models.BooleanField(default=False, db_index=True)
    checkout_date = models.DateTimeField(null=True, db_index=True)
    price = models.PositiveIntegerField(default=0)
    user = models.OneToOneField(User, related_name='fk_one_time_payment_user')
    visitor = models.ForeignKey(User, related_name='fk_one_time_payment_visitor', null=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    # not_deleted = CRMManager()

    class Meta(object):
        db_table = 'one_time_payment'


class PeriodicPayment(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    last_payment = models.DateTimeField(null=True, db_index=True)
    price = models.PositiveIntegerField(default=0, db_index=True)
    user = models.OneToOneField(User, related_name='fk_periodic_payment_user')
    visitor = models.ForeignKey(User, related_name='fk_periodic_payment_visitor', null=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    # not_deleted = CRMManager()  # BUG FIX! Its OK! Don't change

    class Meta(object):
        db_table = 'periodic_payment'


class VisitorFormula(models.Model):
    PERIOD_TYPE = ((0, 'One Time'), (1, 'periodic payment'))
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    formula = models.TextField()
    period_type = models.IntegerField(default=0, choices=PERIOD_TYPE)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'reseller_formula'
        permissions = (('view_reseller_formula', 'Can View Reseller Formula'),)


class DedicatedService(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_service'
        permissions = (('view_dedicated_services', 'Can View Dedicated Services'),)


class DedicatedInvoiceService(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(unique=True, db_index=True)
    price = models.PositiveIntegerField(default=0)
    period = models.IntegerField(default=1)
    service = models.ForeignKey(DedicatedService, related_name='fk_dedicated_invoice_service_service')
    invoice = models.ForeignKey(DedicatedInvoice, related_name='fk_dedicated_invoice_service_invoice')
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_invoice_service'


class DedicatedServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    name = models.CharField(max_length=255, db_index=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    class Meta(object):
        db_table = 'dedicated_service_type'
        permissions = (('view_service_type', 'Can View Dedicated ServiceType'),
                       )


class AssignedDedicatedServiceType(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    service = models.ForeignKey(DedicatedService, related_name='fk_assigned_dedicated_service_type_service')
    service_type = models.ForeignKey(DedicatedServiceType, related_name='fk_assigned_service_type_type')
    history = AuditLog()

    class Meta(object):
        db_table = 'assigned_dedicated_service_type'


class DedicatedServiceFormula(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    dedicated_type = models.ForeignKey(DedicatedServiceType, related_name='fk_dedicated_service_formula')
    formula = models.ForeignKey(VisitorFormula, related_name='fk_dedicated_service_formula_formula')
    history = AuditLog()

    class Meta(object):
        db_table = 'dedicated_service_formula'


class Contracts(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    title = models.CharField(max_length=255)
    message = models.CharField(max_length=500)
    body = models.TextField(null=True)
    is_deleted = models.BooleanField(default=False)
    history = AuditLog()
    objects = CRMManager()

    def delete(self, using=None):
        self.is_deleted = True
        self.save()

    class Meta(object):
        db_table = 'contracts'
        permissions = (('view_contract', 'Can View Contracts'),)


class UserContract(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    accept_date = models.DateTimeField(auto_now=True, null=True)
    user = models.ForeignKey(User, related_name='fk_user_contract_user')
    contract = models.ForeignKey(Contracts, related_name='fk_user_contract_contract')
    history = AuditLog()

    class Meta(object):
        db_table = 'user_contract'


class FloatPackageDiscount(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    charge_amount = models.IntegerField(default=0)
    extra_charge = models.FloatField(default=0.0)
    is_deleted = models.BooleanField(default=False)
    objects = CRMManager()
    history = AuditLog()

    class Meta(object):
        db_table = 'float_service_discount'
        permissions = (('view_float_package_discount', 'View Float Package Discount'),)


class FloatPackageDiscountUsage(models.Model):
    id = models.AutoField(primary_key=True)
    ext = AutoUUIDField(db_index=True, unique=True)
    purchase_date = models.DateTimeField(auto_now=True)
    package_discount = models.ForeignKey(FloatPackageDiscount, related_name='fk_float_package_discount_use_package')
    user = models.ForeignKey(User, related_name='fk_float_package_discount_usage')

    class Meta(object):
        db_table = 'float_service_package_discount'
        permissions = (('view_float_package_usage_history', 'Can View Package Discount History'),)

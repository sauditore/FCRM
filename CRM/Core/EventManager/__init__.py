from django.utils.translation import ugettext as _

from CRM.Core.Events import SystemEventBase, init_events


class NewUserRegisterEventHandler(SystemEventBase):
    def __init__(self):
        super(NewUserRegisterEventHandler, self).__init__()
    name = _('User Register Registration')
    short_name = 'NewUserRegReq'
    code = '7f4c26f2-08cc-4f94-bfa9-31de6c3281ac'


class UnlockAccountEventHandler(SystemEventBase):
    def __init__(self):
        super(UnlockAccountEventHandler, self).__init__()

    name = _('Unlock Locked Account')
    short_name = 'UnlockLockedUserAccount'
    code = '514a2b88-e93f-4c71-894f-023d2b8732a2'


class UserCommentUpdatedEventHandler(SystemEventBase):
    def __init__(self):
        super(UserCommentUpdatedEventHandler, self).__init__()

    name = _('user comment updated')
    short_name = 'UserCommentUpdated'
    code = '1987b256-84e3-4b3c-abc4-fd46d6b8dd8d'


class ReadNotificationEventHandler(SystemEventBase):
    def __init__(self):
        super(ReadNotificationEventHandler, self).__init__()

    name = _('read sent notifications')
    short_name = 'ReadNotification'
    code = 'a78d3dcb-76ad-45c4-b184-0527e03a95c1'


class LoginWithIPEventHandler(SystemEventBase):
    def __init__(self):
        super(LoginWithIPEventHandler, self).__init__()

    name = _('ip login')
    code = 'bfc3bf06-9f7c-4ae2-af67-9da4491c12e8'
    short_name = 'IPLogin'


class InactiveAccountLoginEventHandler(SystemEventBase):
    def __init__(self):
        super(InactiveAccountLoginEventHandler, self).__init__()

    name = _('inactive account login')
    code = 'bf058908-0dab-40ad-a328-833f229cd576'
    short_name = 'InactiveAccountLogin'


class SuperUserCreatedEventHandler(SystemEventBase):
    def __init__(self):
        super(SuperUserCreatedEventHandler, self).__init__()

    name = _('nwe superuser created')
    code = 'ab85b625-f5f7-40ee-a9f0-efdd4b2ab09b'
    short_name = 'SuperUserCreated'


class StaffUserCreatedEventHandler(SystemEventBase):
    def __init__(self):
        super(StaffUserCreatedEventHandler, self).__init__()

    name = _('new personnel created')
    code = 'ee8b4c65-ed05-4005-a6ce-27266d8f914d'
    short_name = 'StaffUserCreated'


class LockUserAccountEventHandler(SystemEventBase):
    def __init__(self):
        super(LockUserAccountEventHandler, self).__init__()

    name = _('user account locked')
    code = '52aa4299-d264-4e82-8d20-0e959ae5df33'
    short_name = 'UserAccountLocked'


class LockIBSAccountEventHandler(SystemEventBase):
    def __init__(self):
        super(LockIBSAccountEventHandler, self).__init__()

    name = _('user ibs account locked')
    code = '5d51932c-59e1-468e-9709-54f7748d4bce'
    short_name = 'UserIBSAccountLocked'


class CallAddNewEventHandler(SystemEventBase):
    def __init__(self):
        super(CallAddNewEventHandler, self).__init__()

    name = _('add new call')
    code = '67580ef6-d45d-4551-a6eb-198c6ad9426f'
    short_name = 'NewSupportCallAdded'


class CallAddNewReferencedEventHandler(SystemEventBase):
    def __init__(self):
        super(CallAddNewReferencedEventHandler, self).__init__()

    name = _('add new referenced call')
    code = '32cd2fab-c67c-46ff-aaeb-e6af4103fa6c'
    short_name = 'NewCallReferencedAdded'


class EquipmentLowAmountEventHandler(SystemEventBase):
    def __init__(self):
        super(EquipmentLowAmountEventHandler, self).__init__()

    name = _('equipment is low')
    code = 'f4df05a5-f1dd-4a45-94bc-d94d33148524'
    short_name = 'EquipmentLowAmount'


class EquipmentNewItemAddedEventHandler(SystemEventBase):
    def __init__(self):
        super(EquipmentNewItemAddedEventHandler, self).__init__()

    name = _('new equipment item added')
    code = 'df96ab1e-13af-4145-8740-a06be33d5666'
    short_name = 'EquipmentNewItem'


class EquipmentOrderAddedEventHandler(SystemEventBase):
    name = _('new equipment order')
    code = 'd5778090-aed3-4773-bac3-5074c624ffa7'
    short_name = 'EquipmentNewOrder'


class TowerReportProblem(SystemEventBase):
    name = _('tower problem')
    code = 'd5778090-aed3-4773-bac3-5074b513aab8'
    short_name = 'ReportTowerProblem'


class UserProfileChanged(SystemEventBase):
    def __init__(self):
        super(UserProfileChanged, self).__init__()

    name = _('User Profile Data Changed')
    short_name = 'UserProfileChanged'
    code = '51aba448-ea14-4c71-894f-023d2b8732a2'


ACTIVE = [NewUserRegisterEventHandler(), CallAddNewReferencedEventHandler(), EquipmentLowAmountEventHandler(),
          EquipmentNewItemAddedEventHandler(), EquipmentOrderAddedEventHandler(),
          CallAddNewEventHandler(), LockIBSAccountEventHandler(),
          InactiveAccountLoginEventHandler(),
          LockUserAccountEventHandler(), UnlockAccountEventHandler(),
          StaffUserCreatedEventHandler(), SuperUserCreatedEventHandler(),
          InactiveAccountLoginEventHandler(), LoginWithIPEventHandler(),
          ReadNotificationEventHandler(), UserCommentUpdatedEventHandler(),
          NewUserRegisterEventHandler(),
          TowerReportProblem(), UserProfileChanged()
          ]


def events_activate_all():
    for a in ACTIVE:
        a.register()
    init_events()

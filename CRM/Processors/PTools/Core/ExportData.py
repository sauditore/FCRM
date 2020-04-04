from CRM import settings
from CRM.models import IBSUserInfo
import vobject
__author__ = 'saeed'


def export_contacts_from_db():
    users = IBSUserInfo.objects.all()
    for u in users:
        user_id = u.ibs_uid
        try:
            print '[INFO] Get User Data For : %s' % user_id
            # user_name = u.user.username
            mobile = u.user.fk_user_profile_user.get().mobile
            holder = vobject.vCard()
            o = holder.add('fn')
            o.value = str(user_id)
            o = holder.add('n')
            o.value = vobject.vcard.Name(family=str(user_id))
            o = holder.add('tel')
            o.type_param = 'cell'
            if not mobile:
                continue
            if len(mobile) < 3:
                continue
            o.value = unicode(mobile)
            f = open(settings.EXPORT_DATA_DIR + '/%s.vcf' % user_id, 'w')
            f.write(holder.serialize())
            print '[INFO] Contact Wrote For %s' % user_id
        except Exception as e:
            print '[ERROR] ' + e.message
            continue

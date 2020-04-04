from email.mime.multipart import MIMEMultipart
import urllib

from django.contrib.auth.models import User

from django.template.context import Context
from django.utils.timezone import now

from CRM.Core.CRMConfig import read_config
from CRM.models import NotifyLog, UserProfile
from CRM.Tools.Validators import validate_integer

from CRM.Tools.Validators import validate_empty_str
from urllib2 import urlopen
from django.utils.translation import ugettext as _
import smtplib
import email.utils
from django.template import Template
__author__ = 'Administrator'


def send_email(text, to_address, title, user_id, is_password=False):
    try:
        n = NotifyLog()
        n.send_time = now()
        n.target = to_address
        if is_password:
            n.description = "***"
        else:
            n.description = text
        n.notify_type = 2
        n.is_read = True
        n.user = User.objects.get(pk=user_id)
        # n.users_user = User.objects.get(email=to_address)
        if to_address is None:
            n.result = False
            n.save()
            return False
        to_email = to_address
        servername = read_config('mail_address')
        username = read_config('mail_username')
        password = read_config('mail_password')
        msg = MIMEMultipart('alternative')
        msg.set_unixfrom('author')
        msg['To'] = email.utils.formataddr(('Recipient', to_email))
        msg['From'] = email.utils.formataddr((title, read_config('mail_username')))
        msg['Subject'] = 'CRM'

        server = smtplib.SMTP(servername, 587)
    except Exception as e:
        print e.message
        return False
    try:
        server.set_debuglevel(True)
        server.ehlo()
        if server.has_extn('STARTTLS'):
            server.starttls()
            server.ehlo()
        server.login(str(username), str(password))
        server.sendmail(read_config('mail_username'), [to_email], msg.as_string())
        n.result = True
        n.save()
    except Exception as e:
        print e.args[1]
    finally:
        server.quit()


def send_text_message(user_id, text, is_password=False):
    if not validate_empty_str(text):
        return False
    if not validate_integer(user_id):
        return False
    text = text.encode('utf-8')
    username = read_config('sms_username')
    print username
    password = read_config('sms_password')
    line = read_config('sms_line')
    username_field = read_config('sms_username_field')
    password_field = read_config('sms_password_field')
    to_field = read_config('sms_target_field')
    text_field = read_config('sms_text_field')
    add_r = read_config('sms_url')
    line_field = read_config('sms_line_field')
    suc = read_config('sms_send_success')
    n = NotifyLog()
    try:
        # text = text.encode()
        user = UserProfile.objects.get(user=user_id)
        if not user.mobile:
            return False
        mobile = user.mobile
        if not add_r.lower().startswith('http://'):
            address = 'http://' + add_r + '?'
        else:
            address = add_r
        if validate_empty_str(line_field) and validate_empty_str(line):
            address = '{0}{1}={2}&'.format(address, line_field, line)
        if validate_empty_str(password_field) and validate_empty_str(password):
            address = '{0}{1}={2}&'.format(address, password_field, password)
        if validate_empty_str(username_field) and validate_empty_str(username):
            address = '{0}{1}={2}&'.format(address, username_field, username)
        if is_password:
            n.description = '***'
        else:
            n.description = text
        n.target = mobile
        n.notify_type = 1
        n.is_read = True
        n.send_time = now()
        n.user = User.objects.get(pk=user_id)
        uc = urllib.urlencode({text_field: text})
        address = '{0}{1}={2}&{3}'.format(address, to_field, mobile, uc)
        res = urlopen(address).read()
        res = str(res)
        if suc in res or suc == res:
            n.result = True
        else:
            n.result = False
    except Exception as e:
        print e.args[0]
        n.result = False
    finally:
        n.save()
        return n.result


def send_inbox(user_id, text, is_password=False):
    try:
        nf = NotifyLog()
        nf.user = User.objects.get(pk=user_id)
        nf.is_read = False
        if is_password:
            nf.description = '***'
        else:
            nf.description = text
        nf.target = _('inbox')
        nf.result = True
        nf.notify_type = 3
        nf.send_time = now()
        nf.save()
        return True
    except Exception as e:
        print e.message
        return False


# 1 : sms , 2 : email , 3 : inbox
def send_notifications(user_id, text, sms=False, mail=True, inbox=True):
    if not validate_integer(user_id):
        return -1
    res = 0
    try:
        profile = UserProfile.objects.get(user=user_id)
        if sms:
            if send_text_message(user_id, text):
                res += 3
        if mail:
            if send_email(text, profile.user.email, 'CRM', user_id):
                res += 1
        if inbox:
            if send_inbox(user_id, text):
                res += 4
        return res
    except Exception as e:
        print e.message
        return res


def __render__(text, params):
    try:
        t = Template(text)
        c = Context(params)
        return t.render(c)
    except Exception as e:
        print e.message
        return ''


def parse_args(args, k):
    if k in args:
        return args[k]
    else:
        '-'

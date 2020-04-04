import email
import datetime
import email.header
import imaplib
import codecs

from CRM.Core.CRMConfig import read_config


class Mail(object):
    def __init__(self, subject, text, html_data, send_date,
                 sender, to, return_path, mail_agent, attachment, original):
        """
        Parsed IMAP Email
        :param subject: Email Subject
        :param text: Message body
        :param html_data: Html Body of message
        :param send_date: Send Date with TZ
        :param sender: Sender Address
        :param to: To Address
        :param return_path: Return path of the mail
        :param mail_agent: Mail Application that mail sent with
        :param attachment: List of attachments
        :param original: original message to future usage
        :return: Mail
        """
        # Performing some type validations
        if not (isinstance(subject, str) or isinstance(subject, unicode)):
            raise TypeError('subject is str or unicode. not %s' % type(subject))
        if not (isinstance(text, str) or isinstance(text, unicode)):
            raise TypeError('text is str or unicode, not %s ' % type(text))
        if not (isinstance(html_data, str) or isinstance(html_data, unicode)):
            raise TypeError('text is str or unicode, not %s ' % type(html_data))
        if not isinstance(send_date, datetime.datetime):
            raise TypeError('send_date is datetime, not %s ' % type(send_date))
        if not (isinstance(sender, str) or isinstance(sender, unicode)):
            raise TypeError('sender is str or unicode, not %s ' % type(sender))
        if not (isinstance(return_path, str) or isinstance(return_path, unicode)):
            raise TypeError('return_path is str or unicode, not %s' % type(return_path))
        if not (isinstance(to, str) or isinstance(to, unicode)):
            raise TypeError('to is str or unicode, not %s ' % type(to))
        if not (isinstance(mail_agent, str) or isinstance(mail_agent, unicode)):
            raise TypeError('mail_agent is str or unicode, not %s ' % type(mail_agent))
        if not (isinstance(attachment, list) or attachment is None):
            raise TypeError('attachment is a list of encoded files or can be None, not %s ' % type(attachment))
        if not (isinstance(original, str) or isinstance(original, unicode)):
            raise TypeError('original is str or unicode, not %s ' % type(original))
        self.__dict__.update({'subject': subject, 'text': text, 'send_date': send_date,
                              'sender': sender, 'to': to, 'agent': mail_agent, 'attachment': attachment,
                              'original': original, 'return_path': return_path, 'html': html_data})
    subject = property(lambda self: self.__dict__.get('subject'))
    text_message = property(lambda self: self.__dict__.get('text'))
    send_date = property(lambda self: self.__dict__.get('send_date'))
    sender = property(lambda self: self.__dict__.get('sender'))
    to = property(lambda self: self.__dict__.get('to'))
    mail_agent = property(lambda self: self.__dict__.get('mail_agent'))
    attachment = property(lambda self: self.__dict__.get('attachment'))
    original = property(lambda self: self.__dict__.get('original'))
    return_path = property(lambda self: self.__dict__.get('return_path'))
    attachment_count = property(lambda self: len(self.attachment))
    html = property(lambda self: self.__dict__.get('html'))

    def save_attachments(self, folder):
        """
        Save all email attachments in a folder. if folder is not exists, then create it.
        :param folder: path to a folder to save data
        :return: None
        """
        if not self.attachment:
            return
        counter = 0
        errors = []
        while counter < len(self.attachment):
            errors.append(self.save_attachment(counter, folder))
            counter += 1
        return errors

    def save_attachment(self, index, folder):
        """
        Save a single attachment by index
        :param index: 0 base index of attachment to save
        :param folder: path to a folder to save
        :return: (res, Exception): (True, None) if operation was success, (False, Exception) if error
        """
        # Some validations....
        if not self.attachment:
            return False, None
        if not isinstance(index, int):
            return False, TypeError('index must be int')
        index = int(index)
        if len(self.attachment) <= index:
            return False, IndexError('index is more than size of attachments')
        atc = self.attachment[index]
        if len(atc) < 1:    # Actually there is nothing here! so return with True!
            return True, None
        data = self.decode(atc[0])  # Decode Content of file
        if not data[0]:  # Result is not OK
            return False, data[1]
        fn = folder + atc[1]    # Folder name + original File name
        f = codecs.open(fn, 'wb')
        f.write(data[1])
        f.close()
        return True, None

    @staticmethod
    def decode(base_64_data):
        try:
            return True, email.base64MIME.decode(base_64_data)
        except Exception as e:
            return False, e.message


class ImportMail(object):
    def __init__(self, user, password):
        if not isinstance(user, str) and not isinstance(user, unicode):
            raise TypeError('Expected str or unicode')
        if not isinstance(password, str) and not isinstance(password, unicode):
            raise TypeError('Expected str or unicode')
        self.__dict__.update({'user': user, 'password': password, 'host': read_config('mail_server', 'mail.gen-co.com'),
                              'https': read_config('mail_https', '1')})
        if self.is_secure:
            self.con = imaplib.IMAP4_SSL(self.__dict__.get('host'))
        else:
            self.con = imaplib.IMAP4(self.__dict__.get('host'))

    username = property(lambda self: self.__dict__.get('user'))
    password = property(lambda self: self.__dict__.get('password'))
    host = property(lambda self: self.__dict__.get('host'))
    is_secure = property(lambda self: self.__dict__.get('https') == '1')

    def connect(self):
        """
        Connect to remote server and login to server
        :return: (result, message) True if login was success, False with error message if failed to login
        """
        try:
            self.con.login(self.username, self.password)
            return True, None
        except Exception as e:
            return False, e.message

    def select(self, box):
        """
        select box. inbox-sent-outbox...
        :param box: str box name
        :return: True if box exists and selected
        """
        try:
            self.con.select(box)
            return True
        except Exception as e:
            print e.message
            return False

    def decode_message(self, msg):
        """
        Decodes messages and returns text, attachment
        :param msg: message to parse
        :return: text_message, list(attachments[(data, file_name)])
        """
        text_part = u''
        html_part = u''
        attach = []
        counter = 0
        for m in msg.get_payload():
            ct = m.get_content_maintype()
            if ct == 'text':
                if m.get_content_type() == 'text/html':
                    html_part += m.get_payload(decode=True).decode('utf-8')
                else:
                    text_part += m.get_payload(decode=True).decode('utf-8')
            elif ct == 'application':
                # Apply encode for utf-8 file names
                attach.append((m.get_payload(), email.header.decode_header(m.get_filename().encode('utf-8'))[0][0]))
            elif ct == 'multipart':
                # another attachment! reprocess
                res = self.decode_message(m)
                text_part += res[0]
                html_part += res[1]
                attach.append(res[2])
            counter += 1
        return text_part, html_part, attach

    def get_unread(self):
        try:
            res = self.con.search(None, '(UNSEEN)')
            if res[0] == 'OK':
                return True, res[1]
            return True, res[1]
        except Exception as e:
            return False, e

    def set_read(self, mail):
        try:
            res = self.con.store(mail, 'FLAGS', '\\Seen')
            if res[0] == 'OK':
                return True, None
            return False, res[1]
        except Exception as e:
            return False, e

    def set_unread(self, mail):
        try:
            res = self.con.store(mail, '-FLAGS', '\\UNSEEN')
            if res[0] == 'OK':
                return True, None
            return False, res[1]
        except Exception as e:
            return False, e

    def process(self, index):
        rv, data = self.con.search(None, index)
        if rv != 'OK':
            return []
        mails = []
        for num in data[0].split():
            rv, data = self.con.fetch(num, '(RFC822)')
            if rv != 'OK':  # Server error!
                print "ERROR getting message", num
                return []
            msg = email.message_from_string(data[0][1])
            date_tuple = email.utils.parsedate_tz(msg['Date'])
            if date_tuple:
                local_date = datetime.datetime.fromtimestamp(
                    email.utils.mktime_tz(date_tuple))
            else:
                local_date = datetime.datetime.today()
            subject = email.header.decode_header(msg['Subject'])[0][0]
            return_path = email.header.decode_header(msg['Return-Path'])[0][0]
            sender = email.header.decode_header(msg['From'])[0][0]
            to = email.header.decode_header(msg['To'])[0][0]
            mailer = email.header.decode_header(msg['X-Mailer'])[0][0]
            if msg.is_multipart():
                # maybe message contains some attachments
                res_x = self.decode_message(msg)
                mails.append(Mail(subject, res_x[0], res_x[1], local_date,
                                  sender, to, return_path, mailer, res_x[2], data[0][1]))
            else:
                # Message is text only
                mails.append(Mail(subject, msg.get_payload(decode=True), '', local_date,
                                  sender, to, return_path, mailer, [], data[0][1]))
        return mails

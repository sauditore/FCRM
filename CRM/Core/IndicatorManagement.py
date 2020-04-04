from datetime import datetime

from django.utils.translation import ugettext as _
from khayyam.jalali_datetime import JalaliDatetime

from CRM.Core.BaseCrmManager import BaseRequestManager
from CRM.Core.CRMConfig import read_config
from CRM.models import LetterFile, PocketBook, IndicatorBook, IndicatorObject


class LetterFileManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': LetterFile})
        super(LetterFileManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name']})

    def search(self):
        name = self.get_search_phrase()
        res = LetterFile.objects.all()
        if name:
            res = res.filter(name__icontains=name)
        return res

    def update(self, force_add=False):
        name = self.get_str('n', True, max_len=255)
        if not name:
            return self.error(_('please enter name'), True)
        x = self.get_single_ext(False)
        if not x:
            x = LetterFile()
        x.name = name
        x.save()


class PocketBookManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': PocketBook})
        super(PocketBookManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'name']})

    def search(self):
        name = self.get_search_phrase()
        res = PocketBook.objects.all()
        if name:
            res = res.filter(name__icontains=name)
        return res

    def update(self, force_add=False):
        name = self.get_str('n', True, max_len=255)
        x = self.get_single_ext()
        if not x:
            x = PocketBook()
        x.name = name
        x.save()


class IndicatorManagement(BaseRequestManager):
    def __init__(self, request, **kwargs):
        kwargs.update({'target': IndicatorBook, 'upload_type': 2})
        super(IndicatorManagement, self).__init__(request, **kwargs)
        self.__dict__.update({'fields': ['pk', 'ext', 'create_date', 'send_date',
                                         'target', 'title', 'has_attachment',
                                         'book_type', 'pocket__name', 'pocket__ext',
                                         'letter_file__name', 'letter_file__ext', 'code',
                                         'receive_date', 'related_person']})

    def search(self):
        target = self.get_search_phrase()
        res = IndicatorBook.objects.all()
        create_date = self.get_date('c', only_date=True)
        send_date = self.get_date('s', only_date=True)
        title = self.get_str('t', max_len=500)
        if target:
            res = res.filter(target__icontains=target)
        if title:
            res = res.filter(title__icontains=title)
        if create_date:
            res = res.filter(create_date=create_date)
        if send_date:
            res = res.filter(send_date=send_date)
        return res

    @classmethod
    def create_send(cls, target, title, has_attachment, sender_id, obj):
        x = IndicatorBook()
        x.user_id = sender_id
        x.send_date = datetime.today()
        x.has_attachment = has_attachment
        x.code = '--'
        lf = read_config('indicator_dedicate_letter', 1)
        pb = read_config('indicator_dedicate_pocket', 1)
        if not LetterFile.objects.filter(pk=lf).exists():
            return False
        if not PocketBook.objects.filter(pk=pb).exists():
            return False
        x.letter_file_id = lf
        x.pocket_id = pb
        x.target = target
        x.title = title
        x.save()
        x.code = cls.generate_code() + '-' + str(x.pk)
        x.save()
        io = IndicatorObject()
        io.content_object = obj
        io.indicator = x
        io.save()
        return True

    @staticmethod
    def generate_code():
        jd = JalaliDatetime.today()
        ix = jd.strftime(read_config('indicator_pattern', '%y-%m'))
        return ix

    def set_received(self):
        dt = self.get_date('rd', True, True)
        x = self.get_single_ext(True)
        if x.receive_date is None:
            x.receive_date = dt
            x.save()

    def update(self, force_add=False):
        send_date = self.get_date('sd', True, True)
        target = self.get_str('t', True, None, 255)
        title = self.get_str('s', True, None, 1024)
        person = self.get_str('rp', False, max_len=255)
        has_attached = self.get_bool('ha', False, False, '1', True)
        book_type = self.get_int('bt', True)
        lmg = LetterFileManagement(self.req, store=self.store)
        lmg.pk_name = 'lf'
        letter_file = lmg.get_single_ext(True)
        pm = PocketBookManagement(self.req, store=self.store)
        pm.pk_name = 'pb'
        pocket_book = pm.get_single_ext(True)
        ix = None
        x = self.get_single_ext()
        if not x:
            x = IndicatorBook()
            ix = self.generate_code()
        # assert isinstance(x, IndicatorBook)
        x.send_date = send_date
        x.target = target
        x.title = title
        x.has_attachment = has_attached
        x.book_type = book_type
        x.letter_file = letter_file
        x.pocket = pocket_book
        x.user = self.requester
        x.related_person = person
        x.save()
        if ix:
            x.code = ix + '-' + str(x.pk)
            x.save()

import tempfile
import time
from CRM.Processors.PTools.DownloadHandler import respond_as_attachment
from CRM.models import CustomOption
from CRM.templatetags.DateConverter import convert_date
from django.utils.translation import ugettext as _
from openpyxl import Workbook

__author__ = 'FAM10'


def export_excel(invoices, request):
    options = CustomOption.objects.all().order_by('group', 'pk')
    option_placement = {}
    position = 0
    cols = [_('id'), _('invoice id'), _('ibs id'), _('name'),
            _('create time'), _('service name'),  # _('current service'),
            _('expire date'), _('price'), _('installation price'), _('bank name'),
            _('pay time'), _('bank ref code'), _('comment')]
    wb = Workbook()
    ws = wb.active
    for o in options:
        cols.append(o.name)
        option_placement.update({o.pk: position})
        position += 1
    ws.append(cols)
    c = 1
    for i in invoices:
        ibs = i.user.fk_ibs_user_info_user.first()
        if ibs:
            ibs_id = ibs.ibs_uid
        else:
            ibs_id = '-'
        data = [c, i.pk, ibs_id, i.user.first_name, convert_date(i.create_time), i.service_text]
        ucs = i.user.fk_user_current_service_user.first()
        if ucs:
            data.append(convert_date(ucs.expire_date))
        else:
            data.append('-')
        data.append(i.price)
        data.append('-')  # Installation Data
        data.append('-')  # Bank Name
        # data.append(_(str(i.is_paid)))
        data.append(convert_date(i.pay_time))
        data.append(i.ref_number)
        data.append(i.comment)
        if hasattr(i.service.content_object, 'fk_float_template_template'):
            if ucs:
                if ucs.is_float:
                    ix = i.service.content_object.fk_float_template_template.order_by('option__group__pk',
                                                                                      'option_id')
                    fx = []
                    loc = 0
                    option_count = options.count() + 1
                    for x in ix:
                        pos = option_placement.get(x.option_id)
                        if pos is None:
                            fx.append(0)
                            loc += 1
                            continue
                        for px in range(loc, option_count):
                            if px == pos:
                                fx.append(x.total_price)
                                loc += 1
                                break
                            else:
                                fx.append(0)
                            loc += 1
                    data += fx
        ws.append(data)
        c += 1
    f = tempfile.NamedTemporaryFile(delete=False)
    wb.save(f.name)
    current_milli = int(round(time.time() * 1000))
    return respond_as_attachment(request, f.name, 'report_%s' % current_milli + '.xlsx')

from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Core.CRMConfig import get_config, set_config, load_config, get_state, read_config
from CRM.Decorators.Permission import multi_check
from CRM.Processors.PTools.Utility import send_error
from CRM.Tools.Validators import get_string, get_integer


@multi_check(just_admin=True, disable_csrf=True)
def config_management(request):
    if request.method == 'GET':
        reload_from_cache = request.GET.get('relocate', '0') == 'YES!PLEASE!'
        conf = get_config()
        data = {}
        sections = conf.sections()
        for s in sections:
            opt = {}
            ox = conf.options(s)
            for o in ox:
                if reload_from_cache:
                    new_config = read_config('%s_%s' % (s, o))
                    set_config(s, o, new_config)
                    dx = {o: new_config}
                else:
                    dx = {o: conf.get(s, o)}
                opt.update(dx)
            data.update({s: opt})
        return render(request, 'configuration/ConfigManagement.html', {'data': data})
    elif request.method == 'POST':
        name = get_string(request.POST.get('name'))
        value = get_string(request.POST.get('value'))
        if not name:
            return send_error(request, _('invalid item'))
        if not value:
            return send_error(request, _('invalid value'))
        section = name.split('__')
        if len(section) < 2:
            return send_error(request, _('invalid value'))
        set_config(section[0], section[1], value)
        load_config(True)
        return HttpResponse('200')
    else:
        return send_error(request, _('invalid method'))


@multi_check(just_admin=True, methods=('GET',), check_refer=False)
def get_config_state(request):
    command = get_integer(request.GET.get('c'))
    if not command:
        return send_error(request, _('invalid command'))
    if command == 1:
        load_config(True)
        return HttpResponse(get_state())
    elif command == 2:
        return HttpResponse(get_state())
    else:
        return send_error(request, _('invalid command'))

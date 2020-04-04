__author__ = 'FAM10'


def is_ajax_request(request):
    return {'is_ajax_request': check_ajax(request)}


def check_ajax(request):
    x = request.META.get('HTTP_X_REQUESTED_WITH')
    pat = ['XMLHttpRequest']
    return x in pat


def is_ip_login(request):
    if hasattr(request, 'ip_login'):
        x = True
    else:
        x = False
    return {'ip_login': x}


def is_switcher_on(request):
    normal_id = request.session.get('normal_id')
    if normal_id is None:
        x = 0
    else:
        x = normal_id
    return {'normal_id': int(x)}

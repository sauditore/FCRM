from django.contrib.auth import logout
from django.core.urlresolvers import reverse
from django.shortcuts import redirect, render

__author__ = 'Administrator'


def frm_logout(request):
    try:
        if request.session.get('normal_id') and request.session.get('target_id'):
            user = request.session['target_id']
            request.session['normal_id'] = None
            request.session['target_id'] = None
            return redirect(reverse('show user navigation menu') + '?uid=%s' % user)
        else:
            logout(request)
            return redirect('/')
    except Exception as e:
        print e.message
        return render(request, 'errors/ServerError.html')

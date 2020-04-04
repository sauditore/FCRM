from datetime import datetime
from django.contrib.auth.models import User
from django.http.response import HttpResponse
from django.shortcuts import render
from CRM.models import UserProfile, NotifyLog

__author__ = 'FAM10'


def receive_sms(request):
    if request.method == 'GET':
        _from = request.GET.get('from')
        _to = request.GET.get('to')
        _text = request.GET.get('text')
        if not _from:
            print 'no from'
            return render(request, 'errors/ServerError.html')
        if not UserProfile.objects.filter(mobile=_from).exists():
            print 'User not found!'
            return render(request, 'errors/ServerError.html')
        try:
            u = User.objects.get(fk_user_profile_user__mobile=_from)
            # assert isinstance(u, User)
            l = NotifyLog()
            l.description = _text
            l.is_read = False
            l.notify_type = 4
            l.send_time = datetime.today()
            l.target = _to
            l.user = u
            l.result = True
            l.save()
            print 'saved'
            return HttpResponse('ok')
        except Exception as e:
            print 'error'
            print e.message
            return render(request, 'errors/ServerError.html')
    else:
        print 'Other methods : %s' % request.method
        return render(request, 'errors/AccessDenied.html')

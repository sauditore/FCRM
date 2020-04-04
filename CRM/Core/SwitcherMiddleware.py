from django.contrib.auth.models import User


class SwitchAccount(object):
    def process_request(self, request):
        normal_id = request.session.get('normal_id')
        target_id = request.session.get('target_id')
        if normal_id and target_id:
            request.user = User.objects.get(pk=target_id)

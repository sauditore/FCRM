import logging
import json

from django.http.response import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _

from CRM.Core.CRMConfig import read_config
from CRM.Processors.PTools.Utility import send_error
from CRM.Tools.Validators import get_integer

logger = logging.getLogger(__name__)


def view_public_dedicated_profit(request):
    if request.method == 'GET':
        return render(request, 'public/ResellerProfit.html')
    elif request.method == 'POST':
        # base_price = 240000
        action = request.POST.get('a')
        if action == '1':
            sell = get_integer(request.POST.get('s').replace(',', ''))
            res = {'internet': int(sell*1.5), 'once': int(sell), 'monthly': int(sell*0.10)}
            return HttpResponse(json.dumps(res))
        elif action == '2':
            is_special = 'cSP' in request.POST
            bw = get_integer(request.POST.get('b'))
            sell = get_integer(request.POST.get('sd').replace(',', ''))
            if is_special:
                min_price = read_config('visitor_special_min', 240000)
                if sell < min_price:
                    return send_error(request, _('min price value is') + ' ' + str(min_price))
            else:
                min_price = read_config('visitor_normal_min', 170000)
                if sell < min_price:
                    return send_error(request, _('min price value is') + ' ' + str(min_price) )
            co_profit = (sell - min_price)*bw   # B9
            if is_special:
                one_time = co_profit*2.2
                monthly = co_profit*0.3
            else:
                one_time = co_profit*2.2
                monthly = co_profit*0.3
            res = {
                   'once': int(one_time),
                   'monthly': int(monthly)
            }
            return HttpResponse(json.dumps(res))
        elif action == '3':
            bw = get_integer(request.POST.get('bi'))
            sell = get_integer(request.POST.get('si').replace(',', ''))
            base_price = read_config('visitor_intranet_base_price', 30000)
            if sell < base_price:
                return send_error(request, _('min price value is') + ' ' + str(base_price))
            co_profit = (sell - base_price) * bw
            one_time = co_profit * 2.2
            monthly = co_profit * 0.3
            return HttpResponse(json.dumps({
                'once': int(one_time), 'monthly': int(monthly)
            }))
        else:
            logger.warning('invalid action requested %s' % action)
            return send_error(request, _('unknown request'))

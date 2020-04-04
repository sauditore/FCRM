# from django.db.models.query_utils import Q
#
# from CRM.Tools.DateParser import parse_date_from_str
# from CRM.models import Invoice
#
# __author__ = 'Amir'
#
#
# def search_invoices(**kwargs):
#     invoices = Invoice.objects.filter(is_deleted=False)
#     for k in kwargs.iterkeys():
#         v = kwargs[k]
#         arg = convert_args(k, v)
#         if not arg:
#             continue
#         if k == 'sd' or k == 'ed':
#             v = parse_date_from_str(kwargs[k][0]).date()
#             arg = convert_args(k, v)
#         if k.startswith('_'):
#             v2 = arg.keys()[0].split(',')
#             f1 = {v2[0]: v[0]}
#             f2 = {v2[1]: v[0]}
#             invoices = invoices.filter(Q(**f1) | Q(**f2))
#         else:
#             invoices = invoices.filter(**arg)
#     # invoices = invoices.filter(is_deleted=True)
#     return invoices
#
#
# def convert_args(k, v):
#     if isinstance(v, list):
#         if not len(v):
#             return {}
#         else:
#             if not v[0]:
#                 return {}
#             else:
#                 v = v[0]
#     args = {'s': 'service', 'si': 'service__in',
#             't': 'package', 'sd': 'pay_time__gt', 'ed': 'pay_time__lt',
#             'pt': 'paid_online', 'ib': 'user__fk_ibs_user_info_user__ibs_uid',
#             'u': 'user', 'ip': 'is_paid', 'pk': 'pk',
#             'sp': 'user__fk_user_current_service_user__service',
#             '-es': 'service',
#             'is': 'ip_static',
#             '_sg': 'service__fk_ibs_service_properties_properties__service__fk_service_group_service__group,package__fk_package_groups_package__group'
#             }
#     if k in args:
#         if k.startswith('-'):
#             if v:
#                 return {args[k]: None}
#             else:
#                 return {}
#         return {args[k]: v}
#     return {}

from CRM.Tools.Validators import validate_input_data_type
from CRM.models import Product, ProductOrder

__author__ = 'FAM10'


def __get_product_args__():
    return {'ss': 'str__serial_number__icontains',
            'sg': 'int__group', 'sb': 'int__brand',
            # 'sn': 'str__name__icontains',
            'avl': 'bool__is_released'}


def __get_order_args__():
    return {'sd': 'date__order_date__gt', 'ir': 'bool__is_ready', 'rsd': 'date__ready_date__gt',
            'u': 'int__user__fk_ibs_user_info_user__ibs_uid',
            'pk': 'int__pk',
            'ed': 'date__order_date__lt', 'pr': 'int__personnel', 'red': 'date__ready_date__lt'}


def search_orders(get):
    if not isinstance(get, dict):
        return ProductOrder.objects.none()
    args = __get_order_args__()
    orders = ProductOrder.objects.all()
    for a in args.iterkeys():
        res = validate_input_data_type(args.get(a), get.get(a))
        if res:
            orders = orders.filter(**res)
    return orders.order_by('-order_date')


def search_products(get):
    if not isinstance(get, dict):
        return Product.objects.none()
    args = __get_product_args__()
    prs = Product.objects.filter(is_deleted=False)
    for a in args.iterkeys():
        res = validate_input_data_type(args.get(a), get.get(a))
        if res:
            prs = prs.filter(**res)
    if get.get('u'):
        prs = prs.filter(is_released=True)
    # Product.objects.get().group.id
    prs = prs.order_by('group')
    return prs

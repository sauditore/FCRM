__author__ = 'Administrator'
from django.template import Library

register = Library()


@register.filter('mul')
def mul(parse, token):
    try:
        return parse * token
    except Exception as e:
        print e.message
        return 0


@register.filter('plus')
def plus(parser, token):
    try:
        return parser + token
    except Exception as e:
        print e.message
        return 0


@register.filter('dev')
def dev(parse, token):
    try:
        return int(parse) / int(token)
    except Exception as e:
        print e.message
        return 0


@register.filter('sub')
def sub(parse, token):
    try:

        return int(parse) - int(token)
    except Exception as e:
        print e.message
        return 0


@register.filter('get_gig_price')
def get_price_value(parse, token):
    try:
        amount = (int(parse) / 1024)
        fp = amount * int(token)
        return fp
    except Exception as e:
        print e.message
        return 0

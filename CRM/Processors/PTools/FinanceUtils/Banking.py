import os
from CRM.Core.Events import fire_event
import CRM.Processors
import CRM.Processors.Finance.Payment
import imp
from CRM.models import Banks, BankProperties

__author__ = 'saeed'


def get_banking_gateways(include_ids=False):
    """
    returns a dict contains banks
    @rtype list
    @return list
    """

    pth = CRM.Processors.Finance.Payment.__path__
    dir_list = os.walk(pth[0]).next()[1]
    banks_data = []
    if include_ids:
        banks_data.append([])
    for bank_dir in dir_list:
        res0 = __get_bank_api_data__(pth[0] + "/" + bank_dir)
        if 'name' not in res0:
            continue
        banks_data.append(res0)
        if include_ids:
            banks_data[0].append(res0.get('identifier'))
    return banks_data


def __get_bank_api_data__(folder_name):
    """
    get a list of bank api data in filename
    @param folder_name: the name of the folder to look for API
    @rtype : dict
    @type folder_name: list
    """
    tmp_res = {}
    try:
        a, b, c = imp.find_module("API", [folder_name])
        banking_api = imp.load_module("", a, b, c)
        name = banking_api.name
        author = banking_api.__author__
        identifier = banking_api.identifier
        properties = banking_api.properties
        tmp_res.update({'name': name, 'author': author, 'identifier': identifier, 'properties': properties})
        return tmp_res
    except ImportError as e:
        print e.message
        return {}


def install_bank_api(bank_identifier):
    """
    Install Bank api to DB
    @param bank_identifier: The bank identifier
    @return:
    """
    try:
        bgw = get_banking_gateways()
        for b in bgw:
            if b.get('identifier') == int(bank_identifier):
                if Banks.objects.filter(internal_value=bank_identifier).exists():
                    bk = Banks.objects.get(internal_value=bank_identifier)
                else:
                    bk = Banks()
                    bk.internal_value = int(bank_identifier)
                bk.name = b.get('name')
                bk.save()
                if BankProperties.objects.filter(bank=bk.pk).exists():
                    bpr = BankProperties.objects.filter(bank=bk.pk)
                    old_names = bpr.values_list('name', flat=True)
                    for p2 in b.get('properties'):
                        if p2 not in old_names:
                            bpr_x = BankProperties()
                            bpr_x.name = p2
                            bpr_x.bank = bk
                            bpr_x.save()
                else:
                    # transaction.set_autocommit(False)
                    for p in b.get('properties'):
                        bpr = BankProperties()
                        bpr.bank = bk
                        bpr.name = p
                        bpr.save()
                    # transaction.commit()
                    # transaction.set_autocommit(True)
                fire_event(6005, bk, None, 1)
                return True
        return False
    except Exception as e:
        print e.message
        # print 'ERROR HERE'
        return False

__author__ = 'Amir'
import logging


class InfoCodes(object):
    def __init__(self):
        pass
    creating_ibs_user = 'CREATE_UFI'
    import_data_from_ibs = 'IMP_IBS_DT'
    core_crm_error = 'CORE_ERROR'
    update_credit = 'CORE_UPDATED_CREDIT'
    update_service = 'CORE_UPDATE_SERVICE'
    core_crm_add_user = 'CORE_CNU'
    core_crm_assign_group = 'CORE_UAG'
    core_banking_pasargad = 'CORE_BNK_PSG'
    core_banking_solver = 'CORE_BNK_RSL'
    core_banking_tracer = 'CORE_BNK_TRC'


class DBLogHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        try:
            pass
        except Exception as e:
            print e.message
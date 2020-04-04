from CRM.IBS.Manager import IBSManager
from CRM.models import IBSService, IBSGroupCharge, IBSIpPool


class ImportDataError(object):
    def __init__(self):
        self.__data__ = ''

    def __add__(self, other):
        self.__data__ += ',' + unicode(other)
        return self

    def get_errors(self):
        return self.__data__


class ImportData(object):
    def __init__(self, ibm):
        if not isinstance(ibm, IBSManager):
            raise TypeError('IBSManager Type Expected')
        self.__ibm__ = ibm
        self.__er__ = ImportDataError()

    def import_all(self):
        pass

    def import_single(self, **kwargs):
        pass

    errors = property(lambda self: self.__er__)


class ImportCharge(ImportData):
    def __init__(self, ibm):
        super(ImportCharge, self).__init__(ibm)

    def import_all(self):
        manager = self.__ibm__
        auth = manager.get_auth_params()
        proxy = manager.get_proxy()
        charges = proxy.charge.listCharges(auth)
        for c in charges:
            x_id = self.import_single(name=c)
            if x_id == 0:
                continue

    def import_single(self, **kwargs):
        er = self.__er__
        if 'name' not in kwargs:
            er += 'invalid name'
            return 0
        name = kwargs.get('name')
        manager = self.__ibm__
        auth = manager.get_auth_params()
        auth['charge_name'] = name
        proxy = manager.get_proxy()
        info = proxy.charge.getChargeInfo(auth)
        if not info:
            er += 'no info for %s' % name
            return 0
        if IBSGroupCharge.objects.filter(ibs_id=info.get('charge_id')).exists():
            c = IBSGroupCharge.objects.get(ibs_id=info.get('charge_id'))
        else:
            c = IBSGroupCharge()
            c.name = info.get('charge_name')
        c.description = info.get('comment')
        c.ibs_id = info.get('charge_id')
        c.ibs_name = info.get('charge_name')
        c.multiple = 0
        c.save()
        return c.pk


class ImportIPPool(ImportData):
    def __init__(self, ibm):
        super(ImportIPPool, self).__init__(ibm)

    def import_single(self, **kwargs):
        name = kwargs.get('name')
        ibm = self.__ibm__
        if not name:
            self.__er__ += 'no name for ip pool'
            return None
        auth = ibm.get_auth_params()
        auth['ippool_name'] = name
        proxy = ibm.get_proxy()
        res = proxy.getIPpoolInfo(auth)
        if IBSIpPool.objects.filter(ibs_id=res.get('ippool_id')).exists():
            pool = IBSIpPool.objects.get(ibs_id=res.get('ippool_id'))
        else:
            pool = IBSIpPool()
            pool.ibs_id = res.get('ippool_id')
        pool.name = res.get('ippool_name')
        pool.comment = res.get('comment')
        pool.save()
        return pool.pk

    def import_all(self):
        ibm = self.__ibm__
        auth = ibm.get_auth_params()
        proxy = ibm.get_proxy()
        pools = proxy.ippool.getIPpoolNames(auth)
        for p in pools:
            self.import_single(name=p)


class ImportGroup(ImportData):
    def __init__(self, ibm):
        super(ImportGroup, self).__init__(ibm)

    def import_all(self):
        manager = self.__ibm__
        proxy = manager.get_proxy()
        auth = manager.get_auth_params()
        groups = proxy.group.listGroups(auth)
        for g in groups:
            self.import_single(name=g)

    def import_single(self, **kwargs):
        if 'name' not in kwargs:
            self.__er__ += 'no name for to import'
            return 0
        manager = self.__ibm__
        proxy = manager.get_proxy()
        auth = manager.get_auth_params()
        auth['group_name'] = kwargs.get('name')
        group = proxy.group.getGroupInfo(auth)
        if not IBSService.objects.filter(ibs_group_id=group.get('group_id')).exists():
            bs = IBSService()
            bs.name = group.get('group_name')
            bs.ibs_group_id = group.get('group_id')
        else:
            bs = IBSService.objects.get(ibs_group_id=group.get('group_id'))
        bs.ibs_name = group.get('group_name')
        bs.save()
        return bs.pk

from datetime import datetime
import os
import urllib2

__author__ = 'Amir'
from hashlib import sha1
try:
    from chilkat import CkRsa, CkByteData, CkString
except:
    chilkat = None
BASE_DIR = os.path.dirname(__file__)


name = 'Pasargad API'
identifier = 3
properties = ["terminal_code", "merchant_code"]


class PasargadAPI(object):
    def __init__(self, terminal_code, merchant_code, redirect_address):
        if not terminal_code:
            raise Exception('please enter terminal code')
        if not merchant_code:
            raise Exception('merchant code is empty')
        if not redirect_address:
            raise Exception('redirect address is empty')
        self.merchant_code = merchant_code
        self.terminal_code = terminal_code
        self.redirect_address = redirect_address
        self.payment_address = 'https://pep.shaparak.ir/gateway.aspx'

    def get_post_params(self, invoice_id, invoice_date, amount):
        if not invoice_id:
            return False
        if not invoice_date:
            return False
        if not amount:
            return False
        try:
            post_time = datetime.today().strftime('%Y/%m/%d %H:%M:%S')
            tmp_data = '#%s#%s#%s#%s#%s#%s#%s#%s#' % (self.merchant_code, self.terminal_code, invoice_id, invoice_date,
                                                      amount, self.redirect_address, 1003,
                                                      post_time)
            # print tmp_data
            sha = sha1(tmp_data)
            key_text = open(BASE_DIR + "/pasargad.pem").read()
            tst = CkRsa()
            tst.UnlockComponent('Start my 30-day Trial')  # RSAT34MB34N_41B1B1DE655Z
            tst.ImportPrivateKey(key_text)
            enc_data = CkByteData()
            digest = CkByteData()
            digest.append2(sha.digest(), len(sha.digest()))
            tst.put_LittleEndian(False)
            tst.SignHash(digest, "SHA-1", enc_data)
            data_0 = CkString()
            enc_data.encode('base64', data_0)
            res = {'merchant_code': self.merchant_code, 'terminal_code': self.terminal_code,
                   'post_time': post_time, 'invoice_id': invoice_id, 'invoice_date': invoice_date,
                   'amount': amount, 'redirect': self.redirect_address, 'cmd': 1003, 'enc': data_0.getString(),
                   'payment_address': self.payment_address}
            return res
        except Exception as e:
            print e.args[0]
            return None

    def check_validation(self, token, price):
        if not token:
            return False
        try:
            data = urllib2.urlopen('https://pep.shaparak.ir/CheckTransactionResult.aspx',
                                   'invoiceUID=%s' % str(token)).read()
            if '<result>True</result>' in data:
                if '<merchantCode>' + self.merchant_code + '</merchantCode>' in data:
                    if '<amount>' + str(price) + '</amount>' in data:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        except Exception as e:
            print e.message
            return False

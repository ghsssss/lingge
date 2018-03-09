import hashlib, requests, arrow, json
import simplejson as json
from  decimal import *
from requests import Session, Request


class ShopCoupon:
    cookies = None
    token = ""

    def __init__(self, item_id, sellerId, price):
        self.url = "http://api.m.taobao.com/h5/mtop.macao.market.activity.applycoupon.querycouponsfordetail/1.0/"
        self.appKey = '12574478'
        self.price = price
        self.item_id = item_id
        self.sellerId = sellerId

    def getData(self):
        # return  r'{"extendParam":"{\"hlFrom\":\"H5_FEED_LIST_OF_BIZ_SOURCE\"}","userType":"1","version":"8.0","app":"tbc","feedId":"2153596","needBizSourceInfo":true,"needAttitudeInfo":true,"needAddViewCnt":true,"needContent":true,"needPromote":false,"needEvaluationInfo":true}'
        d = {'itemId': self.item_id, 'sellerType': 'c', 'from': 'detail', 'sellerId': self.sellerId,
             'ttid': "2016@taobao_h5_2.0.0", "source": "", "userID": ""}
        return json.dumps(d)

    @classmethod
    def setToken(cls, token):
        cls.token = token

    def get_time(self):
        return str(arrow.now().float_timestamp).replace(".", "")[:13]

    @classmethod
    def setCookies(cls, cookies):
        cls.cookies = cookies

    def getParams(self):
        self.params = {
            'v': '1.0',
            'api': 'mtop.macao.market.activity.applycoupon.querycouponsfordetail',
            'appKey': self.appKey,
            't': self.get_time(),
            'ecode': 1,
            'type': 'jsonp',
            'dataType': 'jsonp',
            'callback': 'mtopjsonp1',
            'sign': self.genSign(),
            'data': self.getData()

        }
        return self.params

    def genSign(self):
        m = hashlib.md5()
        s = self.token + "&" + self.get_time() + "&" + self.appKey + "&" + str(self.getData())
        m.update(s.encode("utf-8"))
        return m.hexdigest()

    def http_request(self):

        s = Session()
        req = Request('GET', self.url, params=self.getParams(), cookies=self.cookies)
        prepped = req.prepare()
        prepped.headers['Accept-Language'] = 'zh-CN,zh;q=0.8'
        prepped.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
        prepped.url = prepped.url.replace("%7B", '{')
        prepped.url = prepped.url.replace("%7D", '}')
        resp = s.send(prepped)

        jo = json.loads(resp.text.strip()[11:-1])

        if jo["ret"][0].find('FAIL_SYS') > -1:

            self.setCookies(resp.cookies)
            self.setToken(resp.cookies['_m_h5_tk'].split("_")[0])
            r = self.http_request()

            return r
        elif jo["ret"][0].find('SUCCESS') > -1:

            return jo['data']

    def get_uuid(self):
        r = self.http_request()

        t = Decimal(0)
        uuid = None
        amount=0.0

        if len(r['coupons']) > 0:
            for x in r['coupons'][0]['couponList']:

                y = Decimal("".join(filter(str.isdigit, x['subtitles'][0])))
                if Decimal(self.price) >= y and y > t:
                    t = y
                    uuid = (x['uuid'])
                    amount=x['title']
        return uuid,amount


if __name__ == '__main__':
    a = ShopCoupon(527181579981, 2637269932, 300)
    print(a.get_uuid())

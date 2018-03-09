import requests
from  furl import furl
import arrow
from decimal import *
from  config import *


class Coupon:
    def __init__(self, cookie, reason, item_id, Rate=0, manualAudit=None):
        self.pid = alimama_pid

        self.adzoneid = alimama_adzoneid
        self.siteid = alimama_siteid
        self.cookie = cookie
        self.reason = reason
        self.tb_token = ''
        self.item_id = item_id
        self.amount = 0
        self.manualAudit = manualAudit
        self.Campaign = None
        self.Rate = Rate
        self.set_token()

    def set_token(self):
        for c in self.cookie.split(';'):

            if c.find('_tb_token_') > -1:
                self.tb_token = c[c.find('_tb_token_=') + len('_tb_token_='):]

    def get_serach(self, q, toPage=1, perPageSize=40):

        a = dict(q=q, toPage=toPage, perPageSize=perPageSize, dpyhq=1, auctionTag="", shopTag='dpyhq')
        url = furl('http://pub.alimama.com/items/search.json').add(a)
        r = requests.get(url)

        return r.json()

    def get_coupon(self):
        headers = {'Cookie': self.cookie}
        a = dict(auctionid=self.item_id, adzoneid=self.adzoneid, siteid=self.siteid,
                 t=str(arrow.now().timestamp) + '000', scenes=1,
                 _tb_token_=self.tb_token)
        url = furl('http://pub.alimama.com/common/code/getAuctionCode.json').add(a)
        r = requests.get(url, headers=headers)
        try:
            j = r.json()
        except:
            raise Exception('阿里妈妈过期')
        self.couponShortLinkUrl = j['data']['couponShortLinkUrl']
        self.couponLinkTaoToken = j['data']['couponLinkTaoToken']

    def set_time(self):
        self.effectiveStartTime

    def get_rate(self):

        q = "http://item.taobao.com/item.htm?id=" + str(self.item_id)

        cs = self.get_serach(q=q)['data']['pageList'][0]


        if str(cs['auctionId']) == str(self.item_id):

            if cs['tkSpecialCampaignIdRateMap'] != None :
                if cs['tkRate'] >= float(sorted(cs['tkSpecialCampaignIdRateMap'].values(), reverse=True)[0]) and cs['tkRate'] >= self.Rate:


                    return cs['tkRate']
                else:

                    id = self.item_id
                    cookie = self.cookie
                    headers = {'Cookie': cookie}
                    r = requests.get('http://pub.alimama.com/pubauc/getCommonCampaignByItemId.json?itemId=' + str(id),
                                     headers=headers)
                    try:
                        j = r.json()
                    except:
                        raise Exception("阿里妈妈过期")

                    Campaigns = j['data']
                    if self.manualAudit != None:

                        Campaigns = filter(
                            lambda x: x['manualAudit'] == self.manualAudit and x['commissionRate'] >= self.Rate,
                            Campaigns)
                    else:
                        Campaigns = filter(lambda x: x['commissionRate'] >= self.Rate, Campaigns)
                    Campaigns = list(Campaigns)
                    if (len(Campaigns) == 0):
                        return None
                    Campaigns = sorted(Campaigns, key=lambda x: x['commissionRate'], reverse=True)

                    self.Campaign = sorted(Campaigns, key=lambda x: x['commissionRate'], reverse=True)[0]


                    return float(self.Campaign['commissionRate'])
            elif cs['tkRate'] >= self.Rate:

                return cs['tkRate']
            else:
                return None

        else:
            return None

    def apply_for_promotion_plan(self):
        data = {'campId': self.Campaign['CampaignID'],
                'keeperid': self.Campaign['ShopKeeperID'],
                'applyreason': self.reason,

                '_tb_token_': self.tb_token}
        cookie = self.cookie
        headers = {'Cookie': cookie}
        r = requests.post('http://pub.alimama.com/pubauc/applyForCommonCampaign.json', data=data, headers=headers)
        self.apply_for_promotion = r.json()['ok']


if __name__ == "__main__":
    cookie = 't=61a166d1c721c4e5a4af59ceeb21fbaf;cna=B6V/Edg4F0ECAXHWzuc9cL1P;account-path-guide-s1=true;l=At3d6wpkvYaqTMS-KJBQaOhEbbLXRhFO;isg=AqqqAfH9h2lrTQrx08xbOHem-xDvAC51gXGF2zRj6v2KZ0ohHKt-hfBfkS0G;cookie2=527c8e13861c2c71c01e43c5f67ba8b1;_tb_token_=dpGP1kSliTbq;v=0;cookie32=29ba9b3cbf093c1f1e2c94ddef418c7e;cookie31=MTIyOTk0MTAzLCVFNyU4MSVCNSVFOSU5OCU4MSVFNiU4QSU4MCVFNiU5QyVBRjY2NiwxMDIzNTI1MzkyQHFxLmNvbSxUQg%3D%3D;alimamapwag=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgNi4xOyBXT1c2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzU3LjAuMjk4Ny4xMzMgU2FmYXJpLzUzNy4zNg%3D%3D;login=V32FPkk%2Fw0dUvg%3D%3D;alimamapw=ESFUHXUIEHVaFiUAFHtwEiZxESEkHXYEAwFUOlMGVQ0FVlMFBABQDwkDVlFSUFAEAgpRBlMDUlZU%0AXFVT;'

    c = Coupon(cookie=cookie, reason="申请", item_id=546790408992)
    q = "http://item.taobao.com/item.htm?id=" + str(c.item_id)
    # couponEffectiveEndTime
    # couponEffectiveEndTime
    # zkPrice
    # title
    # biz30day
    # couponAmount
    # tkSpecialCampaignIdRateMap
    print(c.get_rate())

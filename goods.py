from furl import furl
from  models import *
import getdesc
import requests
from decimal import *
import simplejson as json
import top.api
import arrow
import getdetail


class Data:
    def __init__(self, url):
        self.item_id = 0
        self.title = ""
        self.subtitle = ''  # 副标题
        self.platform_type = ''  # {taobao | tmall | chuchutong |alimama }
        self.main_img = ''  # 主图
        self.url = url  # 宝贝链接
        self.promotion_url = ''  # 推广链接
        self.price = Decimal(0)  # 现价文本
        self.original_price = Decimal(0)  # 原价
        self.price_type = ''  # 价格类型
        self.shop_name = ''  # 店铺名

        self.sell_count = ""  # 销量

        self.images = []  # 图片列表
        self.summary_current = ''  # 基本信息
        self.desc = ''  # 详情
        self.coupon_amount = Decimal(0)
        self.begin = arrow.now().datetime
        self.end = arrow.now().datetime
        self.commissionRate = 0.0
        self.CampaignID = ''
        self.CampaignName = ''
        self.status = 0
        self.topic_id = 0
        self.tpwd = ''

        self._clear()

    def check_alimama_item(self):

        if self.url.find('uland.taobao.com/coupon/edetail') > -1 and self.url.find('activityId') > -1:
            f = furl(self.url)
            self.item_id = f.args['itemId']
            activityId = f.args['activityId']
            pid = f.args['pid']
            r = requests.get(furl('https://uland.taobao.com/cp/coupon').add(
                {'itemId': self.item_id, 'activityId': activityId, 'pid': pid}).url).json()

            #self.promotion_url = self.url
            self.url = "http:"+r['result']['item']['shareUrl']


        if self.url.find('uland.taobao.com/coupon/edetail') > -1 and self.url.find('e=') > -1:

            e = furl(self.url).args['e']
            f_coupon = furl('https://uland.taobao.com/cp/coupon').add({'e': e}).url
            r = requests.get(f_coupon)
            json_coupon = r.json()

            tmall = json_coupon['result']['item']['tmall']
            itemId = json_coupon['result']['item']['itemId']

            self.begin = arrow.get(json_coupon['result']['effectiveStartTime']).datetime
            self.end = arrow.get(json_coupon['result']['effectiveEndTime']).datetime
            self.coupon_amount = Decimal(str(json_coupon['result']['amount']))

            self.price= Decimal(str(json_coupon['result']['item']['discountPrice']))
            self.promotion_url = self.url
            if tmall == 1:
                self.url = 'https://detail.tmall.com/item.htm?id=' + str(itemId)
            else:
                self.url = 'https://item.taobao.com/item.htm?id=' + str(itemId)

    def check_chuchutong(self):
        if self.url.find('http') != 0:

            for x in self.url.split(" "):
                if x.find('http') > -1:
                    x = x[x.find('http'):]
                    import requests

                    b = requests.get(x)
                    self.url = b.url

                    self.promotion_url = x

    def _clear(self):

        self.check_alimama_item()
        self._judge_platform_type()
        if self.platform_type == 'tmall':
            f = furl(self.url)
            self.item_id = f.args['id']
            self.url = furl("https://detail.m.tmall.com/item.htm").add({'id': self.item_id}).url
        elif self.platform_type == 'taobao':
            f = furl(self.url)
            self.item_id = f.args['id']
            self.url = furl("http://h5.m.taobao.com/awp/core/detail.htm").add({'id': self.item_id}).url
        elif self.platform_type == "chuchutong":
            self.check_chuchutong()
            f = furl(self.url)
            self.item_id = f.args['productId']

    def _extract_taobao(self):
        """
        提取淘宝宝贝信息
        http://h5.m.taobao.com/awp/core/detail.htm?id=537125061444
        :return: 
        """
        r = getdetail.Detail(self.item_id)
        d = r.http_request()
        self.item_id = d['item']['itemId']
        self.title = d['item']['title']
        self.images = d['item']['images']
        self.main_img = self.images[0]
        try:
            self.subtitle = d['item']['subtitle']
        except:
            self.subtitle = ""

        t = json.loads(d["apiStack"][0]['value'])

        self.sell_count = t['item']['sellCount']

        try:
            top = t["price"]['extraPrices'][0]['priceText']
            top = top[:top.find('-')] if top.find('-') > -1 else top
            self.original_price = Decimal(str(top))
        except:
            self.original_price = self.price

        try:
            self.price_type = t["price"]['priceTag'][0]['text']
        except:
            self.price_type = ''

    def _extract_tmall(self):
        """
        #提取天猫宝贝信息
        http://detail.m.tmall.com/item.htm?id=535986998853
        :return: 
        """

        r = getdetail.Detail(self.item_id)
        d = r.http_request()
        self.item_id = d['item']['itemId']
        self.title = d['item']['title']
        self.images = d['item']['images']
        self.main_img = self.images[0]
        try:
            self.subtitle = d['item']['subtitle']
        except:
            self.subtitle = ""

        t = json.loads(d["apiStack"][0]['value'])
        self.sell_count = t['item']['sellCount']

        try:
            top = t["price"]['extraPrices'][0]['priceText']
            top = top[:top.find('-')] if top.find('-') > -1 else top
            self.original_price = Decimal(str(top))
        except:
            self.original_price = self.price

        try:
            self.price_type = t["price"]['priceTag'][0]['text']
        except:
            self.price_type = ''

    def _extract_chuchutong(self):
        """
        提取楚楚街宝贝信息
        http://m.chuchutong.com/details/detail.html?id=10011445802
        :return: 
        """
        couponId = furl(self.url).args['couponId']

        q = {"channel": "QD_appstore", "package_name": "com.culiukeji.huanletao", "client_version": "3.9.101",
             "ageGroup": "AG_0to24", "client_type": "h5", "api_version": "v5", "imei": "",
             "method": "dwxk_coupon_product", "gender": "1", "token": "", "userId": "", "subChannel": "dwxk",
             "couponId": couponId, "productId": self.item_id, "_ccj_retry_max": 3, "_ccj_retry": 0}

        q = json.dumps(q)
        data = {'data': q}

        r = requests.post(
            "https://product.chuchutong.com/api.php?method=dwxk_coupon_product&couponId=" + couponId + "&product_id=" + str(
                self.item_id) + "&plat_from=h5", data=data)

        d = r.json()["data"]

        self.title = d['product']['cn_title']
        self.begin = d['coupon']['start_time']
        self.end = d['coupon']['end_time']

        self.images = d['product']["image_share_head"]
        self.main_img = d['product']["image_share_head"]

        self.price = Decimal(str(d['product']['sales_price']))
        self.original_price = Decimal(str(d['product']['sales_price']))
        self.coupon_amount = Decimal(str(d['coupon']['facevalue']))

    def setTpwd(self):
        if self.platform_type != 'chuchutong' and self.tpwd == '' and self.promotion_url != '':

            b = top.api.WirelessShareTpwdCreateRequest()
            b.tpwd_param = json.dumps({"url": self.promotion_url, 'text': self.title + 'LingGo', 'logo': self.main_img})

            try:
                resp = b.getResponse()

                self.tpwd = resp['wireless_share_tpwd_create_response']['model']
            except Exception as ex:


                self.tpwd = "未生成"

    def setdesc(self):

        d = getdesc.Desc(self.item_id)
        r = d.http_request()
        self.desc = r['pages']

    def _judge_platform_type(self):
        if self.url.find("tmall.com") != -1:
            self.platform_type = 'tmall'
        elif self.url.find('taobao.com') != -1:
            self.platform_type = 'taobao'
        elif self.url.find('chuchutong') != -1:
            self.platform_type = 'chuchutong'
        else:
            self.platform_type = ''

    def _getinfo(self):
        if self.platform_type == 'taobao':
            self._extract_taobao()
        elif self.platform_type == 'tmall':
            self._extract_tmall()
        elif self.platform_type == 'chuchutong':
            self._extract_chuchutong()

    def getinfo(self):
        try:
            self._getinfo()
        except:
            self._getinfo()

        self.setTpwd()

    def save_to(self):
        """
        保存到数据库
        :return: 
        """

        if Goods.select().where(Goods.item_id == self.item_id).count() > 0:
            return False


        goods = Goods()
        goods.item_id = self.item_id
        goods.title = self.title
        goods.subtitle = self.subtitle
        goods.platform_type = self.platform_type
        goods.main_img = self.main_img
        goods.url = self.url
        goods.promotion_url = self.promotion_url if self.promotion_url != "" else self.url
        goods.price = self.price
        goods.original_price = self.original_price
        goods.shop_name = self.shop_name

        goods.images = self.images
        goods.summary_current = self.summary_current
        goods.price_type = self.price_type
        goods.desc = self.desc

        goods.status = self.status
        goods.topic_id = self.topic_id
        goods.tpwd = self.tpwd
        goods.sell_count = self.sell_count
        goods.coupon_amount = self.coupon_amount
        goods.after_coupon_price = self.price - self.coupon_amount
        goods.begin = self.begin
        goods.end = self.end
        goods.commissionRate = self.commissionRate
        goods.CampaignID = self.CampaignID
        goods.CampaignName = self.CampaignName
        goods.save()
        self.id = goods.id
        return True


if __name__ == "__main__":
    d = Data(
        "https://m.chuchutong.com/details/getcoupons.html?couponId=20399&productId=176000127312&isVideo=0&mKey=v1:29091:170504165303001i0866666825710210:1:0:0:1307711896&from=set")
    d.getinfo()
    print(d.title)
    print(d.promotion_url)

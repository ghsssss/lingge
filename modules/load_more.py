from  furl import furl
import requests
from  flask import request
import gevent
import traceback
from models import *
from  getshopcoupon import ShopCoupon
from  decimal import *


def get_shop_coupon(id,sellerId,price):
    r=ShopCoupon(id,sellerId,price).get_uuid()

    return id,r[0],r[1]


def load_more_moduel():
    q = request.args.get('q', None)
    tid = int(request.args.get('tid', 1))
    p = int(request.args.get('p', 1))
    ord = int(request.args.get('ord', 0))
    order = Goods.id.desc()
    sortType = 0
    queryType = 0
    gs = None

    if ord == 1:
        order = Goods.sell_count.desc()

    elif ord == 2:
        order = Goods.after_coupon_price.asc()
    elif ord == 3:
        order = Goods.coupon_amount.desc()

    if q:
        if ord == 1:

            sortType = 9

        elif ord == 2:
            sortType = 4
        elif ord == 3:
            queryType = 2

        try:
            a = dict(q=q, toPage=p, perPageSize=10, dpyhq=1, auctionTag="", shopTag='dpyhq', startTkRate=30,
                     endPrice=999.99, queryType=queryType, sortType=sortType)
            url = furl('http://pub.alimama.com/items/search.json').add(a)
            r = requests.get(url)

            gs = [{"coupon_amount": x['couponAmount'], 'sellerId': x['sellerId'], "sell_count": x['biz30day'],
                   "main_img": x['pictUrl'],
                   'price': x['zkPrice'],
                   'id': x['auctionId'],
                   'after_coupon_price': x["zkPrice"] - x['couponAmount'], 'platform_type': 'taobao',
                   'title': x['title']} for x in
                  r.json()['data']['pageList']]
            jobs= [gevent.spawn(get_shop_coupon,g['id'],g['sellerId'],g['price']) for g in gs]
            gevent.joinall(jobs)
            gv=[job.value for job in jobs]
            for x in gs:
                for y in gv:

                    if x['id'] == y[0] :
                        if y[1]==None:
                            gs.remove(x)
                        else:

                            x['coupon_amount']=y[2]
                            x['after_coupon_price']=str(Decimal(x["price"]) -Decimal(x['coupon_amount']))







        except Exception as ex:
            print(traceback.print_exc())

            gs = None

    elif tid == 12:
        try:
            gs = Goods.select().where(Goods.after_coupon_price <= Decimal(9.9), Goods.status == 1,
                                      Goods.end > datetime.datetime.now()).order_by(order).paginate(p, 10)

        except Exception as ex:

            gs = None
    else:
        try:
            gs = Goods.select().where(Goods.topic_id == tid, Goods.status == 1,
                                      Goods.end > datetime.datetime.now()).order_by(
                order).paginate(p, 10)
        except Exception as ex:

            gs = None
    return gs

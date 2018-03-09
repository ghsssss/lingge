import requests
from  furl import furl

from decimal import *
from  config import *
import  re
import gevent
from goods import  Data

def get_all_coupon(channel):
    a = dict(st=58, pid=alimama_pid, channel=channel, priceStart=0, priceEnd='', queryCount=200)
    url = furl('https://uland.taobao.com/cp/coupon_list').add(a)
    r = requests.get(url)
    j = r.json()


    totalCount = j['result']['totalCount']


    return j['result']['couponList']


def get_cct(url,tid):
    r=requests.get(url)
    url2=r.url
    d=Data(url2)
    d.getinfo()
    d.topic_id=tid
    d.status=1
    b=d.save_to()
    return b,d.title


def get_all_cct(url,tid):
    r=requests.get(url)
    h=r.text
    link_list = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')",h)
    jobs = [gevent.spawn(get_cct, link,tid) for link in  link_list ]
    gevent.joinall(jobs)
    gv = [job.value for job in jobs]
    return gv



if __name__ == "__main__":
   # c =get_all_coupon(channel="")

   # print(c[1]['item']['shareUrl'])
   c=get_cct('https://share.chuchutong.com/d/LZagJYYn?_from=set',1)

   #c=get_all_cct('https://image-shop.chuchutong.com/culiu.cdn/shop_staticHtml/adSetIndex/18/4/86129_aditemset.html')
   print(c)


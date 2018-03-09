import hashlib, requests, arrow, json
import simplejson as json

from requests import Session, Request


class Detail:
    def __init__(self,itemNumId):
        self.url = "http://acs.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/"

        self.itemNumId =itemNumId
        self.token = ""
    def _getData(self):
        return '{"itemNumId":"' + str(self.itemNumId) + '"}'


    def _getParams(self):
        self.params = {

            'callback': 'mtopjsonp1',
            'type': 'jsonp',

            'data': self._getData()

        }
        return self.params





    def http_request(self):


        s = Session()
        req = Request('GET', self.url, params=self._getParams())
        prepped = req.prepare()
        prepped.headers['Accept-Language']='zh-CN,zh;q=0.8'
        prepped.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0'
        prepped.url = prepped.url.replace("%7B", '{')
        prepped.url = prepped.url.replace("%7D", '}')
        resp = s.send(prepped)

        jo = json.loads(resp.text.strip()[11:-1])


        if jo["ret"][0] == "SUCCESS::调用成功":

            return jo["data"]


if __name__ == "__main__":
    d=Detail("546441289098")
    d.http_request()




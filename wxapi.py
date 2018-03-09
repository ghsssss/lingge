
import requests,json,datetime,time,sign,sys,os

from config import  *



def get_access_token():
    p = {'grant_type': 'client_credential', 'appid': wx_appid, 'secret': wx_secret}
    r = requests.get('https://api.weixin.qq.com/cgi-bin/token', params=p)

    return r.text



def write_access_token(f,token):
    f.truncate()
    f.seek(0)
    json_token = json.loads(token)  # 将http get 转换为 json
    now = datetime.datetime.now()  # 获取当前时间
    expires_time = now + datetime.timedelta(seconds=json_token["expires_in"])  # 获取过期时间
    json_token["expires_in"] = time.mktime(expires_time.timetuple())  # 覆盖过期时间戳
    f.write(json.dumps(json_token))
    f.flush()

def check_access_token():
    f = open(os.path.split(os.path.realpath(__file__))[0]+'/token.txt','r+')
    content=""
    json_txt=""
    try:
        content =f.read();
        json_txt = json.loads(content)
        if(json_txt["expires_in"] < time.time()  ): # 如果超时
            write_access_token(f, get_access_token())


    except Exception as ex :

        write_access_token(f,get_access_token())
        f.seek(0)
        content = f.read();
        json_txt = json.loads(content)

    finally:

        f.close()
    return json_txt


def check_jsticket():
    f = open(os.path.split(os.path.realpath(__file__))[0]+'/jsticket.txt','r+')
    content=""
    json_txt=""
    try:
        content =f.read();
        json_txt = json.loads(content)
        if(json_txt["expires_in"] < time.time()  ): # 如果超时
            write_access_token(f,get_jsticket())


    except Exception as ex :

        write_access_token(f,get_jsticket())
        f.seek(0)
        content = f.read();
        json_txt = json.loads(content)

    finally:

        f.close()
    return json_txt

def get_jsticket():
    token=check_access_token()
    p = {'access_token': token["access_token"], 'type':'jsapi'}
    r = requests.get('https://api.weixin.qq.com/cgi-bin/ticket/getticket', params=p)

    return r.text




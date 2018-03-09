from flask import Flask, request, redirect, url_for, session, flash, g
from flask import render_template
from  goods import  Data
from  getshopcoupon import  ShopCoupon
from modules import  *
from  models import *
from  admin import admin
import simplejson as json
import user
import top.api
import os
from  decimal import *
from  wxapi import *
import ast
import re

top.setDefaultAppInfo(top_appid, top_secret)


app = Flask(__name__)
app.secret_key = 'A0ddfeafeafefjmN]LWX/,?RT'
from  furl import furl

config.UPLOAD_FOLDER = os.path.join(app.root_path, config.UPLOAD_FOLDER)

from flask import send_from_directory


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(config.UPLOAD_FOLDER,
                               filename)


@app.before_request
def before_request():
    if request.path.find('/admin') == 0:

        if session.get('uid', None) == None:
            return redirect(url_for('login'))
    db.connect()


@app.teardown_appcontext
def after_request(response):
    if not db.is_closed():
        db.close()
    return response


@app.route('/init')
def init():
    if not can_init:
        return "can not init"
    db.drop_tables([Goods, Topic, User, AdGroup, Ad], safe=True)
    db.create_tables([Goods, Topic, User, Ad, AdGroup], safe=False)
    Topic.create(id=1, name='综合', title='首页', desc='测试简介简介', img='xx', can_remove=False)
    Topic.create(id=2, name='家居家装', title='家居家装', desc='', img='xx', can_remove=False)
    Topic.create(id=3, name='数码家电', title='数码家电', desc='', img='', can_remove=False)
    Topic.create(id=4, name='母婴', title='母婴', desc='', img='', can_remove=False)
    Topic.create(id=5, name='食品', title='食品', desc='', img='', can_remove=False)
    Topic.create(id=6, name='女装', title='女装', desc='', img='', can_remove=False)
    Topic.create(id=7, name='鞋包配饰', title='鞋包配饰', desc='', img='', can_remove=False)
    Topic.create(id=8, name='美装个护', title='美装个护', desc='', img='', can_remove=False)
    Topic.create(id=9, name='男装', title='男装', desc='', img='', can_remove=False)
    Topic.create(id=10, name='内衣', title='内衣', desc='', img='', can_remove=False)
    Topic.create(id=11, name='聚优惠', title='聚优惠', desc='', img='', can_remove=False)
    Topic.create(id=12, name='9.9包邮', title='9.9包邮', desc='', img='', can_remove=False)
    Topic.create(id=13, name='好货推荐', title='好货推荐', desc='', img='', can_remove=False)
    AdGroup.create(id=1, name='首页焦点图')
    AdGroup.create(id=2, name='方块广告位')
    AdGroup.create(id=3, name='banner图')
    Ad.create(id=1, url="/", img='/static/img/b.png', index=1, adgroup_id=2)
    Ad.create(id=2, url="/", img='/static/img/b.png', index=2, adgroup_id=2)
    Ad.create(id=3, url="/", img='/static/img/b.png', index=3, adgroup_id=2)
    Ad.create(id=4, url="/", img='/static/img/b.png', index=4, adgroup_id=2)

    user.create('admin', '123456')
    return 'ok'


@app.route('/')
def index():
    q = request.args.get('q')

    tid = int(request.args.get('tid', 1))
    if q:

        return render_template('index.html', q=q)
    elif tid == 1:

        ads_1 = Ad.select().where(Ad.adgroup_id == 1).order_by(Ad.index)
        ads_2 = [0, 0, 0, 0, 0, 0]
        ads_2[1] = Ad.get(Ad.adgroup_id == 2, Ad.index == 1)
        ads_2[2] = Ad.get(Ad.adgroup_id == 2, Ad.index == 2)
        ads_2[3] = Ad.get(Ad.adgroup_id == 2, Ad.index == 3)
        ads_2[4] = Ad.get(Ad.adgroup_id == 2, Ad.index == 4)

        ads_3 = Ad.select().where(Ad.adgroup_id == 3).order_by(Ad.index)

        return render_template('index.html', tid=tid, ads_1=ads_1, ads_2=ads_2, ads_3=ads_3)
    else:
        return render_template('index.html', tid=tid)


@app.route('/load_more')
def index_load_more():

    gs=load_more_moduel()

    if gs != None and len(gs) > 0:
        return render_template('load_more.html', gs=gs)
    else:
        return "None"

@app.route('/test')
def test():
    import top.api
    req = top.api.TbkItemGetRequest()
    req.fields = "coupon_click_url"
    req.q = "女装"



    req.page_no = 123
    req.page_size = 20
    try:
        resp = req.getResponse()

        return resp
    except Exception as e:
        print(e)




@app.route('/goods/<int:id>')
def goods(id):
    sellerId=request.args.get('sellerId',0)
    if sellerId ==0:
        g = Goods.get(Goods.id == id)
        # if g.platform_type == 'chuchutong':
        #    return  redirect(g.promotion_url)

        if request.user_agent.string.lower().find("micromessenger") == -1 or g.platform_type == 'chuchutong':
            return redirect(g.promotion_url)
        desc = ast.literal_eval(g.desc)

        return render_template('goods.html', g=g, desc=desc)
    else:
        zkPrice=request.args.get('zkPrice',0)
        s=ShopCoupon(id,sellerId,zkPrice)
        acid=s.get_uuid()

        url = 'https://uland.taobao.com/coupon/edetail?activityId={0}&itemId={1}&pid={2}'.format(acid, id,config.alimama_pid)
        d=Data(url)
        d.getinfo()
        if request.user_agent.string.lower().find("micromessenger") == -1 or d.platform_type == 'chuchutong':
            return redirect(d.promotion_url)
        d.setdesc()

        d.after_coupon_price =  d.price -  d.coupon_amount
        d.images=str(d.images)
        desc =d.desc

        return render_template('goods.html', g=d, desc=desc)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        u = user.login(username, password)

        if u != None:

            session['uid'] = u.id
            return redirect(url_for('admin.index'))
        else:
            flash("用户名或者密码错误")
            return redirect(url_for('login'))


    else:
        return render_template('login.html')


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('uid', None)
    return redirect(url_for('login'))


@app.route('/get_wx_conf')
def get_wx_conf():
    jsticket = check_jsticket()
    jsticket = jsticket['ticket']
    s = sign.Sign(jsticket, request.referrer)
    ss = s.sign()
    appid = config.wx_appid
    return render_template('get_wx_conf.html', ss=ss, appid=appid)


@app.errorhandler(500)
def handle_exception(error):
    db.close()
    return "error"


@app.template_filter('json_loads')
def json_loads(string):
    string = string.replace("'", '"')

    o = json.loads(string)
    return o


@app.template_filter('coonvert_dec')
def coonvert_dec(d):
    d = Decimal(d).quantize(Decimal('0.00'))  # python3.5下有问题 所以加上的补丁

    sd = str(d)

    i, p = sd.split('.')

    if p=='00':
        return i
    elif p[1] == '0':
        return i+"."+p[0]


    else:
        return sd


@app.template_filter('title_t')
def title_t(s, tolen):
    pattern = re.compile(r'<.*?>')
    s=pattern.sub('', s)
    tl = 0
    ts = ''
    for x in s:

        l = 2 if len(x.encode('utf-8')) > 1  else 1
        if tl + l + 3 >= tolen:

            return ts + '...'
        else:
            ts = ts + x
            tl = tl + l
    return ts


@app.context_processor
def topics():
    TOPICS = Topic.select()

    return dict(TOPICS=TOPICS)


app.register_blueprint(admin, url_prefix='/admin')

if __name__ == '__main__':
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(host='127.0.0.1', debug=True)

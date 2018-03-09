from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.utils import secure_filename
from goods import Data
from  models import *
import load_excel, os, random, string
import user
from coupon import Coupon
from  decimal import *
from  collect import get_all_coupon,get_all_cct
import traceback
import arrow

admin = Blueprint('admin', __name__, template_folder='templates/admin')


@admin.route('/', methods=['POST', "GET"])
@admin.route('/index', methods=['POST', "GET"])
def index():
    if request.method != 'POST':
        total = Goods.select().count()
        total2 = Goods.select().where(Goods.end > datetime.datetime.now()).count()
        return render_template('admin/index.html', total=total, total2=total2)
    q = request.form.get('q')
    gs = []

    if q:
        q = '%' + q + '%'
        gs = Goods.select().where(Goods.title % q)
    return render_template('admin/index.html', gs=gs)


@admin.route('/list_topic/<int:tid>')
def list_topic(tid):
    p = int(request.args.get('p', 1))
    gs = Goods.select().where(Goods.topic_id == tid).order_by(Goods.id.desc()).paginate(p, 10)
    topic = Topic.get(Topic.id == tid)
    return render_template('list_topic.html', gs=gs, topic=topic, p=p)


@admin.route('/preadd', methods=['POST', "GET"])
def preadd():
    try:
        url = request.form["url"]
        if url == '':
            raise ('url None')
        tid = request.form["tid"]

        d = Data(url)
        d.getinfo()
    except:
        flash('输入有误！')
        return redirect(request.referrer)

    return render_template("preadd.html", data=d, tid=tid)


@admin.route('/add', methods=['POST'])
def add():
    url = request.form['promotion_url']

    d = Data(url)
    d.getinfo()
    d.title = request.form['title']
    d.subtitle = request.form['subtitle']
    d.begin = arrow.get(request.form['begin']).datetime
    d.end = arrow.get(request.form['end']).datetime

    d.promotion_url = request.form['promotion_url']
    d.coupon_amount = Decimal(request.form.get('coupon_amount', 0))
    d.tpwd = request.form['tpwd']
    d.status = int(request.form['status'])
    # d.permanent = False if request.form['permanent'] == 'yes' else False

    d.topic_id = request.form['tid']
    if d.platform_type != "chuchutong":
        d.setdesc()

    d.save_to()
    return redirect(url_for('admin.list_topic', tid=d.topic_id))


@admin.route('/goods_delete/<int:id>')
def goods_delete(id):
    g = Goods.delete().where(Goods.id == id)
    g.execute()
    return redirect(request.referrer)


@admin.route('/topic_purge/<int:tid>')
def topic_purge(tid):
    g = Goods.delete().where(Goods.topic_id == tid)
    g.execute()
    return redirect(url_for('admin.list_topic', tid=tid))


@admin.route('/status_update/<int:id>', methods=['POST', 'GET'])
def status_update(id):
    status = int(request.args['status'])
    goods = Goods.get(Goods.id == id)
    goods.status = status
    goods.save()
    return redirect(request.referrer)


@admin.route('/upload_excel', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        try:
            tid = int(request.form['tid'])
            file = request.files['file']

            load_excel.load(file, tid)

            return redirect(url_for('admin.list_topic', tid=tid))
        except:
            flash('输入有误，请重试')
            return redirect(url_for('admin.upload_excel'))
    else:
        topics = Topic.select()

        return render_template('upload_excel.html', topics=topics)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config.ALLOWED_EXTENSIONS


@admin.route('/preview/<int:id>', methods=['POST', "GET"])
def preview(id):
    goods = Goods.get(Goods.id == id)

    return render_template("preview.html", goods=goods)


@admin.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method != 'POST':
        return render_template('reset_password.html')
    else:
        pw = request.form['pw']
        pw2 = request.form['pw2']

        if pw != pw2 or pw == "":
            flash('密码不相符！')
            return render_template('reset_password.html')
        uid = session['uid']
        u = User.get(User.id == uid)
        u.password = user._sha256(pw)
        u.save()
        flash('修改成功')
        return render_template('reset_password.html')


@admin.route('/ad_add/<int:gid>', methods=['GET', 'POST'])
def ad_add(gid):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        url = request.form['url']
        index = int(request.form['index'])
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename) and url:
            filename = secure_filename(file.filename)
            a, b = os.path.splitext(filename)
            f = a + '_' + ''.join(random.sample(list(string.ascii_letters), 5)) + b

            file.save(os.path.join(config.UPLOAD_FOLDER, f))
            fulr = url_for('uploaded_file', filename=f)

            Ad.create(img=fulr, url=url, adgroup_id=gid, index=index)
            return redirect(url_for('admin.ad_list', gid=gid))
    else:
        adg = AdGroup.get(AdGroup.id == gid)
        return render_template('admin/ad_add.html', adg=adg)


@admin.route('/ad_update/<int:id>', methods=['GET', 'POST'])
def ad_update(id):
    if request.method == 'POST':
        # check if the post request has the file part
        ad = Ad.get(Ad.id == id)
        ad.url = request.form['url']
        ad.index = request.form['index']

        file = request.files['file']
        # file = request.files.get('file',None)
        # if user does not select file, browser also
        # submit a empty part without filename

        if file.filename != '' and file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            a, b = os.path.splitext(filename)
            f = a + '_' + ''.join(random.sample(list(string.ascii_letters), 5)) + b

            file.save(os.path.join(config.UPLOAD_FOLDER, f))
            fulr = url_for('uploaded_file', filename=f)
            ad.img = fulr

        ad.save()
        return redirect(url_for('admin.ad_list', gid=ad.adgroup_id))
    else:
        ad = Ad.get(Ad.id == id)
        return render_template('admin/ad_update.html', ad=ad)


@admin.route('/ad_list/<int:gid>')
def ad_list(gid):
    ads = Ad.select().where(Ad.adgroup_id == gid).order_by(Ad.index)
    adg = AdGroup.get(AdGroup.id == gid)

    return render_template('admin/ad_list.html', ads=ads, adg=adg)


@admin.route('/ad_delete/<int:id>')
def ad_delete(id):
    ad = Ad.get(Ad.id == id)
    ad.delete_instance()
    return redirect(url_for('admin.ad_list', gid=ad.adgroup.id))


@admin.route('/auto_collect', methods=['POST', 'GET'])
def auto_collect():
    if request.method != 'POST':
        topics = Topic.select()
        return render_template('admin/auto_collect.html', topics=topics)
    else:
        channel = request.form['channel']
        topic_id = request.form['topic_id']
        reason = request.form['reason']
        cookie = request.form['cookie']
        rate = float(request.form['rate'])
        manualAudit = request.form['manualAudit']
        if manualAudit == '0':
            manualAudit = 0
        else:
            manualAudit = None

        item_index = request.form['item_index']
        try:

            c = get_all_coupon(channel=channel)
            total = len(c)
            next_index = int(item_index) + 1
            if next_index >= total:
                next_index = 0

            url = c[(0 - int(item_index))]['item']['shareUrl']
            d = Data('http:' + url)
            c = Coupon(cookie, reason, d.item_id, rate, manualAudit)
            cam = c.get_rate()

            if cam == None:
                return jsonify(message="不符合要求，跳过", title=d.title,
                               item_index=item_index, total=total, next_index=next_index)
            d.commissionRate = cam
            d.getinfo()
            d.topic_id = int(topic_id)
            d.status = 1
            d.setdesc()
            is_saved = d.save_to()
            if not is_saved:
                return jsonify(message="宝贝重复", title=d.title,
                               item_index=item_index, total=total, next_index=next_index, rate=d.commissionRate)
            if c.Campaign != None:
                try:
                    c.apply_for_promotion_plan()
                except:
                    print(traceback.print_exc())
                    d.commissionRate = -1
            d.save_to()
            return jsonify(message="采集成功", title=d.title,
                           item_index=item_index, total=total, next_index=next_index, rate=d.commissionRate)

        except Exception as ex:
            print(traceback.print_exc())

            return jsonify(message="采集失败 ：" + str(ex), item_index=item_index, total=total, next_index=next_index)


@admin.route('/bulk_collect', methods=['POST', 'GET'])
def bulk_collect():
    if request.method != 'POST':
        topics = Topic.select()
        return render_template('admin/bulk_collect.html', topics=topics)
    else:
        urls = request.form['urls']

        topic_id = request.form['topic_id']
        reason = request.form['reason']
        cookie = request.form['cookie']
        rate = float(request.form['rate'])
        manualAudit = request.form['manualAudit']
        if manualAudit == '0':
            manualAudit = 0
        else:
            manualAudit = None

        item_index = request.form['item_index']
        try:

            total = len(urls.split())
            url = urls.split()[int(item_index)]
            next_index = int(item_index) + 1
            if next_index >= total:
                next_index = 0

            d = Data(url)
            c = Coupon(cookie, reason, d.item_id, rate, manualAudit)
            cam_rate = c.get_rate()
            print(cam_rate)
            if cam_rate == None:
                return jsonify(message="不符合要求，跳过", title=d.title,
                               item_index=item_index, total=total, next_index=next_index)

            d.commissionRate = cam_rate
            d.getinfo()
            d.topic_id = int(topic_id)
            d.status = 1
            d.setdesc()
            is_saved = d.save_to()
            if not is_saved:
                return jsonify(message="宝贝重复", title=d.title,
                               item_index=item_index, total=total, next_index=next_index, rate=d.commissionRate)

            try:
                if c.Campaign != None:
                    c.apply_for_promotion_plan()
            except:
                d.commissionRate = -1



            return jsonify(message="采集成功", title=d.title,
                           item_index=item_index, total=total, next_index=next_index, rate=d.commissionRate)

        except Exception as ex:
            print(traceback.print_exc())

            return jsonify(message="采集失败 ：" + str(ex), item_index=item_index, total=total, next_index=next_index)

@admin.route('/cct_collect', methods=['POST', 'GET'])
def cct_collect():
    if request.method != 'POST':
        topics = Topic.select()
        return render_template('admin/cct_collect.html', topics=topics)
    else:
        urls = request.form['urls']
        topic_id = request.form['topic_id']
        gv=get_all_cct(urls,topic_id)
        return redirect(url_for('admin.list_topic',tid=topic_id))


from peewee import *
import datetime
import config

db = MySQLDatabase(host=config.database['host'],
                   port=config.database['port'],
                   user=config.database['user'],
                   passwd=config.database['passwd'],
                   database=config.database['database'],
                   charset='utf8'
                   )


class BaseModel(Model):
    class Meta:
        database = db


class Topic(BaseModel):
    id = PrimaryKeyField()
    name = CharField()
    title = CharField()
    img = CharField()
    desc = CharField()
    can_remove = BooleanField()


class Goods(BaseModel):
    id = PrimaryKeyField()
    item_id = CharField(null=False)
    title = CharField()
    subtitle = CharField()
    platform_type = CharField()
    main_img = CharField()
    url = TextField(null=False)
    promotion_url = TextField()
    price = DecimalField(decimal_places=2)
    price_type = CharField()
    original_price = DecimalField(decimal_places=2)
    shop_name = CharField()
    images = TextField()
    summary_current = TextField()
    sell_count = IntegerField()
    desc = TextField()
    created = DateTimeField(default=datetime.datetime.now)
    tpwd = CharField()  # 淘口令
    coupon_amount = DecimalField(decimal_places=2)
    after_coupon_price = DecimalField(decimal_places=2)
    begin = DateTimeField()
    end = DateTimeField()
    commissionRate=FloatField(default=0.0)
    CampaignID=CharField(default="")
    CampaignName=TextField(default="")
    Exist=BooleanField(default=False) #是否申请高佣金

    status = IntegerField()

    topic = ForeignKeyField(Topic)


class Config(BaseModel):
    id=PrimaryKeyField()
    tb_token=TextField()
    cookie=TextField()


class User(BaseModel):
    id = PrimaryKeyField()
    username = CharField()
    password = CharField()


class AdGroup(BaseModel):
    id = PrimaryKeyField()
    name = TextField()


class Ad(BaseModel):
    id = PrimaryKeyField()
    url = TextField()
    img = TextField()
    index = IntegerField()
    adgroup = ForeignKeyField(AdGroup)

import xlrd
from io import BytesIO, StringIO

from decimal import *
import goods


def load(file, tid):
    xls = xlrd.open_workbook(file_contents=file.read())
    table = xls.sheets()[0]
    nrows = table.nrows
    for i in range(1, nrows):

        try:

            data = goods.Data(table.cell(i, 3).value)
            data.getinfo()
            data.setdesc()
            data.promotion_url = table.cell(i, 25).value
            data.tpwd = table.cell(i, 24).value  # 淘口令

            ca = table.cell(i, 20).value

            if ca.find('减') > -1:
                data.coupon_amount = Decimal(ca[ca.find('减') + 1:-1])
            else:
                data.coupon_amount = Decimal(ca[:ca.find('元')])

            data.topic_id = tid
            data.status = 1
            data.save_to()
            #data.apply_for_promotion_plan(cookie,reason)
        except Exception as ex:

            pass

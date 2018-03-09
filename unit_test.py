import unittest
import  goods
import  getdetail
class Test_extract_tmall(unittest.TestCase):

    def test_tmall(self):
        url='https://detail.m.tmall.com/item.htm?spm=a220m.1000858.1000725.9.fHiyQF&id=522639449656&skuId=3450127555381&areaId=330400&user_id=228784630&cat_id=2&is_b=1&rn=d70c7f64eb391576623b3a9d04c332ac'
        data =goods.Data(url)
        data.getinfo();

        self.assertEqual(data.title, '裂帛2017春夏文艺刺绣针织运动长裤松紧腰直筒休闲裤女51151414')


class TestTaoBaoApi(unittest.TestCase):
    def test(self):
        a= getdetail.TaoApi()
        a.itemNumId=546719026913
        d=a.http_request()



if __name__ == '__main__':
    unittest.main()
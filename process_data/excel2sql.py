#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__: stray_camel

import xlrd,sys,os,logging
absPath = os.path.abspath(__file__)   #返回代码段所在的位置，肯定是在某个.py文件中
temPath = os.path.dirname(absPath)    #往上返回一级目录，得到文件所在的路径
temPath = os.path.dirname(temPath)    #在往上返回一级，得到文件夹所在的路径
sys.path.append(temPath)
from geo.geo_map import Geo_mapInterface
from public import config
#sys.path.insert(0, temPath)          #也可以使用这种方式，确定tmpPath为最高级搜索路径
class Excel2Sql(object):
    def __init__(
        self, 
        url:"str类型的文件路径", 
        sheet:"excel中的表单名"):
        self.f_name = url
        # 将excel中特定表单名数据存储起来
        self.sh_data = xlrd.open_workbook(self.f_name).sheet_by_name(sheet)
        self.rows = self.sh_data.nrows
        self.cols = self.sh_data.ncols
    def test(self):
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.info("test")
            return 1
    def init_SampleViaProvince_name(
        self, 
        Province_name:"省名"
        ) ->"insert的数据，列表形式[('地域名1','1','经纬度'),('地域名2','1','经纬度')]":
        geo_app = Geo_mapInterface(config.geo_key)
        all_data = [self.sh_data.row_values(i) for i in range(self.rows)]
        
        cities_data=[[["".join(i),1],["".join(i[1:len(i)]),1]][i[0]==i[1]] for i in all_data if i[0] == Province_name]
        for i in cities_data:
            i.append(geo_app.get_coordinatesViaaddress("".join(i[0])))
        # cities_data=[[["".join(i),1,'test1'],["".join(i[1:len(i)]),1,'test2']][i[0]==i[1]] for i in all_data if i[0] == Province_name]
        return cities_data
    
if __name__ == "__main__":
    test = Excel2Sql(config.src_path+"\\data\\2019最新全国城市省市县区行政级别对照表(194).xls","全国城市省市县区域列表")
    print(test.init_SampleViaProvince_name("北京市"))
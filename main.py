#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__: stray_camel

import os,sys
import xlrd
from op_postgresql import opsql
from public import config
from process_data import excel2sql
from geo import geo_map

def generate_sampledata():
    # 定义excel中操作对象excel_data
    excel_data = excel2sql.Excel2Sql(config.src_path+"\\data\\2019最新全国城市省市县区行政级别对照表(194).xls","全国城市省市县区域列表")
    all_cities = excel_data.sh_data
    # 获取excel_data的数据总量
    print(all_cities.nrows,all_cities.ncols)
    # data = [all_cities.row_values(i) for i in range(15,22)]
    # 定义数据库操作对象
    op_postgre = opsql.OperationDbInterface()
    # 获取插入样表数据的sql语句，并插入数据
    data_insert_sample = excel_data.init_SampleViaProvince_name("湖北省")
    # print("获取湖北省的数据",data_insert_sample)
    result = op_postgre.insert_sample_data("insert into sample_data(address,ad_type,coordinates) values (%s,%s,%s)",data_insert_sample)
    # 初始化样表
    # result =op_postgre.ini_table("sample_data")
    if result['code']=='0000':
        print("操作数据{}条，操作：{}!".format(result['data'],result['message']))
    else:
        print(result)

if __name__ == "__main__":
    # generate_sampledata()
    op_postgre = opsql.OperationDbInterface()
    addList = op_postgre.select_all("sample_data")['data']
    test = geo_map.Geo_mapInterface()
    print(addList)
    # print(test.key)
    # all_test = test.get_disViaCoordinates(addList)
    all_test = {'origin': ['湖北省武汉市江岸区', '湖北省武汉市江岸区', '湖北省武汉市江汉区'], 'destination': ['湖北省武汉市江汉区', '湖北省武汉市乔口区', '湖北省武汉市乔口区'], 'distance': ['1520', '9197', '7428'], 'route': [['台北一路', '新华路'], ['台北一路', '台北路', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '二环线辅路', '沿河大道'], ['新华路', '建设大道', '建设大道', '建设大道', '建设大道', '沿河大道']]}
    # print(all_test)
    # for x in range(len(all_test)-1):
    #     print(x)
    #     data = [str(all_test[i][x]) for i in all_test]
    #     print(data)
    all_data = [[str(all_test[i][x]) for i in all_test] for x in range(len(all_test)-1)]
    print(all_data)
    result = op_postgre.insert_sample_route("insert into sample_route(origin,destination,distance,route) values (%s,%s,%s,%s)",all_data)
    # 初始化样表
    # result =op_postgre.ini_table("sample_route")
    # if result['code']=='0000':
    #     print("操作数据{}条，操作：{}!".format(result['data'],result['message']))
    # else:
    #     print(result)
#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__: stray_camel
import urllib.request #发送请求
from urllib import parse #URL编码
import json,logging,jsonpath,sys,os
absPath = os.path.abspath(__file__)   #返回代码段所在的位置，肯定是在某个.py文件中
temPath = os.path.dirname(absPath)    #往上返回一级目录，得到文件所在的路径
temPath = os.path.dirname(temPath)    #在往上返回一级，得到文件夹所在的路径
sys.path.append(temPath)
from public import config

class Geo_mapInterface(object):
    def __init__(self,
    key:"高德地图apikey值" = '3e2235273dd2c0ca2421071fbb96def4'):
        self.addList = [('湖北省武汉市江岸区', 1, '114.278760,30.592688'), ('湖北省武汉市江汉区', 1, '114.270871,30.601430'), ('湖北省武汉市乔口区', 1, '114.214920,30.582202')] #创建一个列表存放地址数据
        # self.dict = dict(set(self.addList))#创建一个字典用于存放地址经纬度数据
        self.key = key

    def get_coordinatesViaaddress(self, 
    address:"地点名"
    ) -> "返回str类型的经纬度":
        url='https://restapi.amap.com/v3/geocode/geo?address='+address+'&output=json&key='+self.key
        #将一些符号进行URL编码
        newUrl = parse.quote(url, safe="/:=&?#+!$,;'@()*[]")
        coor = json.loads(urllib.request.urlopen(newUrl).read())['geocodes'][0]['location']
        logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        logger = logging.getLogger(__name__)
        logger.info("查询{}的经纬度：{}！".format(address,coor))
        # print()
        return coor

    def get_disViaCoordinates(self,
    addList:"一个列表存放地址数据"
    ) ->  "{'origin':[],'destination':[],'distance':[],'route':[]}":
        dict_route = {'origin':[],'destination':[],'distance':[],'route':[]}
        for m in range(len(addList)):    
            for n in range(m,len(addList)):
                if m!=n:
                    print('get_tetst',m,n)
                    #从addList中得到地址的名称，经纬度
                    origin = addList[m][2]
                    destination = addList[n][2]
                    url2='https://restapi.amap.com/v3/direction/driving?origin='+origin+'&destination='+destination+'&extensions=all&output=json&key=3e2235273dd2c0ca2421071fbb96def4'
                #编码
                    newUrl2 = parse.quote(url2, safe="/:=&?#+!$,;'@()*[]")
                    #发送请求
                    response2 = urllib.request.urlopen(newUrl2)
                    #接收数据
                    data2 = response2.read()
                    #解析json文件
                    jsonData2 = json.loads(data2)
                    #输出该json中所有road的值
                    # print(jsonData2)
                    road=jsonpath.jsonpath(jsonData2,'$..road')
                    #从json文件中提取距离
                    distance = jsonData2['route']['paths'][0]['distance']
                    #字典dict_route中追加数据
                    dict_route.setdefault("origin",[]).append(addList[m][0])
                    dict_route.setdefault("destination",[]).append(addList[n][0])
                    dict_route.setdefault("distance",[]).append(distance)
                    dict_route.setdefault("route",[]).append(road)
        return dict_route


if __name__ == "__main__":
    test = Geo_mapInterface()
    print(test.key)
    print(test.get_disViaCoordinates(test.addList))
    # print(test.get_coordinatesViaaddress('湖北省武汉市洪山区'))
# dict_route={"出发地":[],"目的地":[],"距离":[],"线路":[]}
# k = len(addList) #nameList列表中元素个数

    
# print(dict_route)

# print(dict(([1,2], i )for i in range(2)))


# 城市距离爬取-任务计划
> 本地创建数据库，将excel数据存储到city表中，再取|湖北省|的所有地级市和县、县级市、区数据作为样表数据记录在样表中。

博客地址：[https://boywithacoin.cn/](https://boywithacoin.cn/ "https://boywithacoin.cn/")
项目的完整地址在[https://github.com/Freen247/python_get_cityDistance](https://github.com/Freen247/python_get_cityDistance "https://github.com/Freen247/python_get_cityDistance")
有兴趣的可以给我评论和star/issue哦?~ (ง •_•)ง

本地创建数据库，将excel数据存储到city表中，再取|湖北省|的所有地级市和县、县级市、区数据作为样表数据记录在样表中。准备工作创建好public/config.py扩展包，到时候，利用python的xlrd包，定义process_data包来存放操作excel数据，生成sql语句的类，
定义op_postgresql包来存放数据库的操作对象，定义各种方法
创建crwler包，来存放爬虫的操作对象 -> 发现对方网站调用的地图api -> 更改为调用德地图api的包-存放操作对象
创建log文件夹，存放数据库操作的日志
创建data文件夹，存放初始excel数据

## 数据库基本构造：
样本数据表格式：
表名：sample_table

|name|column|data type|length|分布|fk|必填域|备注|
| :------------ | :------------ | :------------ | :------------ | :------------ | :------------ | :------------ | :------------ |
|地域名|address|text|   |   |   |TRUE|地域名|
|地域类型|ad_type|integer|   |   |   |TRUE|0-为地级市；1-为县、县级市、区。|
|经纬度|coordinates|text|   |   |   |TRUE|地域名的经纬度|
|···|   |   |   |   |   |   |   ||

样本1-1地点route表的格式

表名:sample_route

|name|column|data type|length|分布|fk|必填域|备注|
| :------------ | :------------ | :------------ | :------------ | :------------ | :------------ | :------------ | :------------ |
|出发点|origin|text|   |   |   |   |出发点|
|目的点|destination|text|   |   |   |   |目的点|
|距离|distance|integer|   |   |   |   |距离|
|路线|route|text|   |   |   |   |路线|
|···|   |   |   |   |   |   |   ||


## 创建配置信息接口
> 方便存储我们需要的特定变量和配置信息。

**public/config.py**

```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__: stray_camel

import os,sys
#当前package所在目录的上级目录
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
```

## 创建读取excel数据的接口
> 利用python的xlrd包，定义process_data包来存放操作excel数据，生成sql语句的类

[参考github源码readme文档](https://github.com/python-excel/xlrd/blob/master/README.md "参考文档")
并没有发现在PyPI上有document，所以只能去github上找源码了，xlrd处理excel基础guide
```python
import xlrd
book = xlrd.open_workbook("myfile.xls")
print("The number of worksheets is {0}".format(book.nsheets))
print("Worksheet name(s): {0}".format(book.sheet_names()))
sh = book.sheet_by_index(0)
print("{0} {1} {2}".format(sh.name, sh.nrows, sh.ncols))
print("Cell D30 is {0}".format(sh.cell_value(rowx=29, colx=3)))
for rx in range(sh.nrows):
print(sh.row(rx))
```
创建process_data/excel2sql.py扩展包，方便后面import
获取excel的数据构造sql语句，创建city表（湖北省）样表

**process_data/excel2sql.py**
```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__: stray_camel

import xlrd,sys,os,logging
from public import config
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
```

当我们生成这个Excel2Sql对象的时候，我们希望按照类似

```python
excel_data = excel2sql.Excel2Sql("fiel_name","sheet_name")
```

的代码形式来直接读取excel文件并获取某个表单的数据。所以在初始化对象的时候我们希望对其属性进行赋值。

excel表中，我们按照下面的形式进行存储数据：

|省/直辖市|地级市	| 县、县级市、区| 
| ------------ | ------------ |------------ |	
|北京市	|北京市	|东城区|	
|...|... |... |

![](/static/media/editor/TIM截图20191224215625_20191224215644286792.png)

之后我们希望通过调用这个类（接口）地时候能够访问其中一个函数，只获取某个省/或者直辖市的所有数据，类似湖北省，我们指向获取奇中103个县、区。

在类Excel2Sql中定义方法：

```python
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
```

之后我们可以测试类的构造是否正确，或进行调试：
在文件末端编写：

```python
if __name__ == "__main__":
    test = Excel2Sql(config.src_path+"\\data\\2019最新全国城市省市县区行政级别对照表(194).xls","全国城市省市县区域列表")
    print(test.init_SampleViaProvince_name("北京市"))
```

测试结果：

```bash
(env) PS F:\览众数据> & f:/览众数据/env/Scripts/python.exe f:/览众数据/城市距离爬取/process_data/excel2sql.py
[['北京市东城区', 1, '116.416357,39.928353'], ['北京市西城区', 1, '116.365868,39.912289'], ['北京市崇文区', 1,
'116.416357,39.928353'], ['北京市宣武区', 1, '116.365868,39.912289'], ['北京市朝阳区', 1, '116.601144,39.948574'], ['北京市丰台区', 1, '116.287149,39.858427'], ['北京市石景山区', 1, '116.222982,39.906611'], ['北京市海淀区', 1, '116.329519,39.972134'], ['北京市门头沟区', 1, '116.102009,39.940646'], ['北京市房山区', 1, '116.143267,39.749144'], ['北京市通州区', 1, '116.656435,39.909946'], ['北京市顺义区', 1, '116.654561,40.130347'], ['北京市昌
平区', 1, '116.231204,40.220660'], ['北京市大兴区', 1, '116.341014,39.784747'], ['北京市平谷区', 1, '117.121383,40.140701'], ['北京市怀柔区', 1, '116.642349,40.315704'], ['北京市密云县', 1, '116.843177,40.376834'], ['北京
市延庆县', 1, '115.974848,40.456951']]
```











## 创建OP数据库postgresql（其他数据库也都一样啦~）接口
> 定义op_postgresql包来存放数据库的操作对象，定义各种方法

数据库的curd真的是从大二写到大四。
访问postgresql数据库一般用的包：psycopg2
[访问官网](https://pypi.org/project/psycopg2/ "访问官网")
[在这个操作文档网站中，使用的思路已经很清楚的写出来了http://initd.org/psycopg/docs/usage.html](http://initd.org/psycopg/docs/ "http://initd.org/psycopg/docs/usage.html")
![](/static/media/editor/TIM截图20191224221014_20191224221026915442.png)

希望大小少在网上走弯路（少看一些翻译过来的文档）。。。
[http://initd.org/psycopg/](http://initd.org/psycopg/ "http://initd.org/psycopg/")

模式还是一样，调用postgresql的驱动/接口，设置参数登陆，访问数据库。设置光标，注入sql数据，fetch返回值。

- 这里需要注意的几点是，默认防xss注入，写代码时一般设置参数访问。
- 注意生成日志文件，打印日志

具体过程不赘述，直接上代码

**op_postgresql/opsql.py**:
```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__: stray_camel

'''
定义对mysql数据库基本操作的封装
1.数据插入
2.表的清空
3.查询表的所有数据
'''
import logging
import psycopg2
from public import config
class OperationDbInterface(object):
    #定义初始化连接数据库
    def __init__(self, 
    host_db : '数据库服务主机' = 'localhost', 
    user_db: '数据库用户名' = 'postgres', 
    passwd_db: '数据库密码' = '1026shenyang', 
    name_db: '数据库名称' = 'linezone', 
    port_db: '端口号，整型数字'=5432):
        try:
            self.conn=psycopg2.connect(database=name_db, user=user_db, password=passwd_db, host=host_db, port=port_db)#创建数据库链接
        except psycopg2.Error as e:
            print("创建数据库连接失败|postgresql Error %d: %s" % (e.args[0], e.args[1]))
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG,format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        self.cur=self.conn.cursor()
        
    #定义在样本表中插入数据操作
    def insert_sample_data(self, 
    condition : "insert语句" = "insert into sample_data(address,ad_type,coordinates) values (%s,%s,%s)", 
    params : "insert数据，列表形式[('地域名1','1','经纬度'),('地域名2','1','经纬度')]" = [('地域名1','1','经纬度'),('地域名2','1','经纬度')]
    ) -> "字典形式的批量插入数据结果" :
        try:
            self.cur.executemany(condition,params)
            self.conn.commit()
            result={'code':'0000','message':'执行批量插入操作成功','data':len(params)}
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.info("在样本表sample_data中插入数据{}条，操作：{}!".format(result['data'],result['message']))
        except psycopg2.Error as e:
            self.conn.rollback()  # 执行回滚操作
            result={'code':'9999','message':'执行批量插入异常','data':[]}
            print ("数据库错误|insert_data : %s" % (e.args[0]))
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return result
    
```

继续写（代码长了，怕显示出错）
```python
    #定义在sample_route表中插入数据操作
    def insert_sample_route(self, 
    condition : "insert语句" ,
    params : "insert语句的值"
    )->"字典形式的批量插入数据结果":
        try:
            self.cur.executemany(condition,params)
            self.conn.commit()
            result={'code':'0000','message':'执行批量插入操作成功','data':len(params)}
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.info("在样本表sample_route中插入数据{}条，操作：{}!".format(result['data'],result['message']))
        except psycopg2.Error as e:
            self.conn.rollback()  # 执行回滚操作
            result={'code':'9999','message':'执行批量插入异常','data':[]}
            print ("数据库错误|insert_data : %s" % (e.args[0]))
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return result

    #定义对表的清空
    def ini_table(self,
    tablename:"表名")->"清空表数据结果":
        try:
            rows_affect = self.cur.execute("select count(*) from {}".format(tablename))
            test = self.cur.fetchone()  # 获取一条结果
            self.cur.execute("truncate table {}".format(tablename))
            self.conn.commit()
            result={'code':'0000','message':'执行清空表操作成功','data':test[0]}
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.info("清空{}表，操作数据{}条，操作：{}!".format(tablename,result['data'],result['message']))
        except psycopg2.Error as e:
            self.conn.rollback()  # 执行回滚操作
            result={'code':'9999','message':'执行批量插入异常','data':[]}
            print ("数据库错误|insert_data : %s" % (e.args[0]))
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return result
    
    #查询表的所有数据
    def select_all(self, 
    tablename:"表名")->"返回list，存放查询的结果":
        try:
            rows_affect = self.cur.execute("select * from {}".format(tablename))
            test = self.cur.fetchall()  
            # self.cur.execute("truncate table {}".format(tablename))
            self.conn.commit()
            result={'code':'0000','message':'查询表成功','data':test}
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.info("清空{}表，操作数据{}条，操作：{}!".format(tablename,result['data'],result['message']))
        except psycopg2.Error as e:
            self.conn.rollback()  # 执行回滚操作
            result={'code':'9999','message':'执行批量插入异常','data':[]}
            print ("数据库错误|insert_data : %s" % (e.args[0]))
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
        return result
    #数据库关闭
    def __del__(self):
        self.conn.close()
```

这里提出来想说一下的打印日志文件的操作，：
参考文件：
https://docs.python.org/zh-cn/3/library/logging.config.html?highlight=logging
https://docs.python.org/zh-cn/3/library/logging.html?highlight=logging#module-logging
logging作为python老牌库，在[https://docs.python.org/zh-cn/3/library/index.html](https://docs.python.org/zh-cn/3/library/index.html "https://docs.python.org/zh-cn/3/library/index.html")中一般都搜索的到，参数的说明不过多的赘述。
因为我的代码都是用utf-8写的所以在basicConfig配置时，加入了utf-8的信息。

```python
result={'code':'9999','message':'执行批量插入异常','data':[]}
            print ("数据库错误|insert_data : %s" % (e.args[0]))
            logging.basicConfig(stream=open(config.src_path + '/log/syserror.log', encoding="utf-8", mode="a"), level = logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
            logger = logging.getLogger(__name__)
            logger.exception(e)
```

## 测试爬取`https://licheng.supfree.net/`网站
> 测试`https://licheng.supfree.net/`网站是否可以传参进行post，获取request后的两地的地理距离

- 测试网站是否有反爬虫机制，结果无。

通过测试request，设置测试地点洪山区和江夏区，网站显示距离为16.5公里
解析html发现
测试结果：网站的数据是通过js文件获取传参的。

```python
var map = new BMap.Map("container");
map.centerAndZoom(new BMap.Point(116.404, 39.915), 14);

var oGl = document.getElementById("div_gongli");
var ofname = document.getElementById("tbxArea");
var otname = document.getElementById("tbxAreaTo");
if (ofname.value != "" && otname.value != "") {
	var output = "全程：";
	var searchComplete = function(results) {
		if (transit.getStatus() != BMAP_STATUS_SUCCESS) {
			return;
		}
		var plan = results.getPlan(0);
		output += plan.getDistance(true); //获取距离
		output += "/";
		output += plan.getDuration(true); //获取时间
	}
	var transit = new BMap.DrivingRoute(map, {
		renderOptions: {
			map: map,
			panel: "results",
			autoViewport: true
		},
		onSearchComplete: searchComplete,
		onPolylinesSet: function() {
			oGl.innerText = output;
		}
	});
	transit.search(ofname.value, otname.value);
}
...

```
我们查看网站加载的js文件，发现获取Bmap这个对象原来是来自于
```
https://api.map.baidu.com/?qt=nav&c=131&sn=2%24%24%24%24%24%24%E6%B4%AA%E5%B1%B1%E5%8C%BA%24%240%24%24%24%24&en=2%24%24%24%24%24%24%E6%B1%9F%E5%A4%8F%E5%8C%BA%24%240%24%24%24%24&sy=0&ie=utf-8&oue=1&fromproduct=jsapi&res=api&callback=BMap._rd._cbk35162&ak=zS6eHWhoEwXMUrQKkaaTlvY65XsVykFf
```
很明显，这个网站也是调用的百度的api。
我们查看js文件传递的部分参数：
```
content: {dis: 16538,…}
dis: 16538
kps: [{a: 7, dr: "", dw: 0, ett: 17, ic: "", iw: 0, pt: ".=zl83LBgOCJVA;", rt: 1, tt: 1},…]
rss: [{d: 0, g: "", n: "", rr: 0, t: 0, tr: 0},…]
taxi: {detail: [{desc: "白天(05:00-23:00)", kmPrice: "2.3", startPrice: "14.0", totalPrice: "47"},…],…}
time: 1516
toll: 0
...
```
**核实content里的dis和time是否就是网站显示的距离和时间**
当我们更换测试地点后，显示的距离和https://api.map.baidu.com 中content的内容一样
time：1516%60=25.26666666666667‬，和显示的26分钟也是核对的。

测试结果：网站没有反爬虫机制，但是调用的是百度地图pai获取数。

- 网站储存地址的数据是按照编码来的，对应的下级城市为小数
比如热门城市：
```
hot_city: ["北京市|131", "上海市|289", "广州市|257", "深圳市|340", "成都市|75", "天津市|332", "南京市|315", "杭州市|179", "武汉市|218",…]
0: "北京市|131"
1: "上海市|289"
2: "广州市|257"
3: "深圳市|340"
4: "成都市|75"
5: "天津市|332"
6: "南京市|315"
7: "杭州市|179"
8: "武汉市|218"
9: "重庆市|132"
```
当测试区级地点：（洪山区、江夏区）
```
map.centerAndZoom(new BMap.Point(116.404, 39.915), 14);
```


- 如果不行能否调用高德地图api？

### 创建接口-调用高德地图api
在高德的管理平台注册个人开发：https://lbs.amap.com/dev/key/app
![](/static/media/editor/TIM截图20191224221759_20191224221810982550.png)

申请个人的key。每日调用量有上线，所以只能一点点的做。
我们将申请到的key写入配置信息文件中：
public/config.py
```python
#!/usr/bin/python
# -*- coding: utf-8 -*-
#__author__: stray_camel

import os,sys
#当前package所在目录的上级目录
src_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
geo_key = '3e2235273ddtestdef4'
#key我已经打马赛克了，请自己去申请
```

完成功能：
通过地域名查询经纬度；
对出发/目的地点-路程-路线，数据进行查询，并插入到数据库中，现已实现。但对于数据量较多的情况，数据库的操作较慢。

首先前往高德地图注册个人用户，获取一个key，之后我们可以通过构造url，通过request来获取数据。

通过address获取经纬度：
```python
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
```

通过城市list获取两点之间距离和出行方式：
```python
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
```


数据库样品：
sample_table

数据库的内容我就用json表示了哈：
```json
[
  {
    "address": "湖北省武汉市江岸区",
    "ad_type": 1,
    "coordinates": "114.278760,30.592688"
  },
  {
    "address": "湖北省武汉市江汉区",
    "ad_type": 1,
    "coordinates": "114.270871,30.601430"
  },
  {
    "address": "湖北省武汉市乔口区",
    "ad_type": 1,
    "coordinates": "114.214920,30.582202"
  },
  ...共103条地点数据
```

sample_route，以sample_table前三个数据为例做出查询，和返回。
```json
[
  {
    "origin": "湖北省武汉市江岸区",
    "destination": "湖北省武汉市江汉区",
    "route": "['台北一路', '新华路']",
    "distance": "1520"
  },
  {
    "origin": "湖北省武汉市江岸区",
    "destination": "湖北省武汉市乔口区",
    "route": "['台北一路', '台北路', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '解放大道', '二环线辅路', '沿河大道']",
    "distance": "9197"
  },
  {
    "origin": "湖北省武汉市江汉区",
    "destination": "湖北省武汉市乔口区",
    "route": "['新华路', '建设大道', '建设大道', '建设大道', '建设大道', '沿河大道']",
    "distance": "7428"
  }
]
```

------------
BUG:
问题：在process_data/excel2sql.py，调用格比public/config.py接口
问题：当我们访问隔壁文件夹的接口时，如果发现调用不了，可以在当前文件的头部加入：
```python
import sys,os
absPath = os.path.abspath(__file__)   #返回代码段所在的位置，肯定是在某个.py文件中
temPath = os.path.dirname(absPath)    #往上返回一级目录，得到文件所在的路径
temPath = os.path.dirname(temPath)    #在往上返回一级，得到文件夹所在的路径
sys.path.append(temPath)
```
将当前文件夹所在的路径加入到python系统路径中
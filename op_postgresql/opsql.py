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


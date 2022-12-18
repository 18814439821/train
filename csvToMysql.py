import csv
import pymysql

# 链接数据库
conn = pymysql.connect(host='127.0.0.1', port=3306, user='root',
                       password='', db='echarts', charset='utf8', connect_timeout=1000)
# 创建数据库对象
cursor = conn.cursor()
# 创建总表
sql = 'create table if not exists 诈骗数据 (id int NOT NULL AUTO_INCREMENT, schoolName varchar(255),' \
      ' fraudWay varchar(255), money int, month varchar(255), time varchar(255), PRIMARY KEY (`id`))'
cursor.execute(sql)
with open(r'/srv/shixun/static/诈骗数据.csv', 'r', encoding='utf-8') as csv1:
    reader = csv.DictReader(csv1)
    # 清空表
    sql2 = 'truncate table 诈骗数据'
    cursor.execute(sql2)
    for row in reader:
        money = str(row['诈骗金额'])
        schoolName = row['高校名称']
        if '为由' in row['诈骗方式']:
            fraudWay = row['诈骗方式'].replace('')
        fraudWay = row['诈骗方式']
        month = row['诈骗月份']
        time = row['文章发布时间']
        # print(schoolName)
        # print(fraudWay)
        # print(money)
        # print(time)
        # 执行插入表数据语句
        sql3 = 'INSERT INTO 诈骗数据 (schoolName, fraudWay, money, month, time) VALUES (%s,%s,%s,%s,%s)'
        cursor.execute(sql3, (schoolName, fraudWay, money, month, time))
conn.commit()
# 高校总诈骗次数和金额（univCount）
sql_univCount = 'create table if not exists univCount (univName varchar (255),' \
                'count int, money int, primary key (`univName`))'
cursor.execute(sql_univCount)
sql_univCount1 = 'truncate table univCount'
cursor.execute(sql_univCount1)
sql_univCount2 = 'INSERT INTO univCount SELECT DISTINCT schoolName univName,' \
                 'count(*) count, sum(money) money FROM 诈骗数据 GROUP BY schoolName'
cursor.execute(sql_univCount2)
# 月份总诈骗金额 (monthMoney)
sql_monthMoney = 'create table if not exists monthMoney (month varchar(255),' \
                 'money int, count int, primary key (`month`))'
cursor.execute(sql_monthMoney)
sql_monthMoney1 = 'truncate table monthMoney'
cursor.execute(sql_monthMoney1)
sql_monthMoney2 = 'insert into monthMoney select distinct month month,' \
                  'sum(money) money , count(month) count from 诈骗数据 group by month'
cursor.execute(sql_monthMoney2)
# 诈骗类型发生总次数和金额 (fraudwayCount)
sql_fraudwayCount = 'create table if not exists fraudwayCount (fraudway varchar(255),' \
                    'count int, money int, primary key (`fraudway`))'
cursor.execute(sql_fraudwayCount)
sql_fraudwayCount1 = 'truncate table fraudwayCount'
cursor.execute(sql_fraudwayCount1)
sql_fraudwayCount2 = 'insert into fraudwayCount select fraudWay fraudway,' \
                     'count(*) count, sum(money) money from 诈骗数据 group by fraudWay'
cursor.execute(sql_fraudwayCount2)
# 创建副表
sql4 = 'create table if not exists alldata (data varchar(255), primary key (`data`))'
cursor.execute(sql4)


with open(r'/srv/shixun/static/爬取高校警情数据.csv', 'r', encoding='utf-8') as csv2:
    reader = csv.DictReader(csv2)
    sql4_1 = 'truncate table alldata'
    cursor.execute(sql4_1)
    for row in reader:
        data = row['诈骗信息']
        sql4_2 = 'insert into alldata(data) value (%s)'
        cursor.execute(sql4_2, data)
conn.commit()
conn.close()

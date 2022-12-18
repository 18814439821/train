import csv

import os.path
import pprint
import re
import time
from datetime import datetime

from lxml import etree
import pymysql

import pandas as pd
import requests


def infoHandler(cookies, referer, url):
    # 要求爬出2022一整年的数据
    timestamp4nextYear = datetime.fromtimestamp(time.mktime(time.strptime('2023-1-1 0:0:0', '%Y-%m-%d %H:%M:%S')))
    timestamp4thisYear = datetime.fromtimestamp(time.mktime(time.strptime('2021-12-31 23:59:59', '%Y-%m-%d %H:%M:%S')))
    oldData = None
    file = r'/srv/shixun/static/广州天河公安文章.csv'
    tempfile = r'/srv/shixun/static/广州天河公安文章_temp.csv'
    if os.path.exists(file):
        oldData = pd.read_csv(file)
        print(oldData)
    f = open(tempfile, mode='w+', encoding='utf-8', newline='')
    csv_writer = csv.DictWriter(f, fieldnames=['标题', '文章发布时间', '文章地址'])
    csv_writer.writeheader()
    parts = str(url).split('begin=0')
    print(parts)
    lefturl = parts[0] + 'begin='
    righturl = parts[1]
    headers = {
        'cookie': cookies,
        'referer': referer,
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edg/107.0.1418.62'
    }
    flag = False
    for page in range(0, 80, 4):
        url = lefturl + f'{page}' + righturl
        # 请求页面 获取响应的json数据（json数据中app_msg_list存放者文章信息）
        response = requests.get(url=url, headers=headers)
        html_data = response.json()
        pprint.pprint(response.json())
        lis = html_data['app_msg_list']
        # 遍历app_msg_list
        for li in lis:
            # 获取标题链接和发布时间 打包成字典 DictWriter写入
            title = li['title']
            link_url = li['link']
            update_time = li['update_time']
            timeArray = time.localtime(int(update_time))
            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
            dit = {
                '标题': title,
                '文章发布时间': otherStyleTime,
                '文章地址': link_url,
            }
            # 判定当前时间是否在今年内 若否 则跳出循环
            timestamp4thispage = datetime.fromtimestamp(update_time)
            if not timestamp4thisYear < timestamp4thispage < timestamp4nextYear:
                print('2022 done')
                flag = True
                break
            if '天河区打击治理' in dit['标题']:
                csv_writer.writerow(dit)
                print(dit)
        if flag:
            break
        time.sleep(10)
    f.close()
    lastData = pd.read_csv(tempfile)
    # 如果先前未爬取过数据 那么oldData应为None
    if oldData is None:
        differce_info = lastData
    else:
        # 合并两个 DataFrame,并去除重复值 以得到差集
        differce_info = pd.concat([lastData, oldData]).drop_duplicates(keep=False)
    # 最新爬取的数据tempfile覆盖写入file
    with open(tempfile, mode='r', encoding='utf-8', newline='') as tempfile, open(file, mode='w', encoding='utf-8',
                                                                                  newline='') as file:
        source_contents = tempfile.read()
        file.write(source_contents)

    print('输出差集')
    print(differce_info)
    Xpath = '//*[@id="js_content"]/section[16]/section[2]/p//text()'
    XpathV1 = '//*[@id="js_content"]/section[17]/section[2]/p//text()'
    XpathV2 = '//*[@id="js_content"]/section[18]/section[2]/p//text()'
    XpathV3 = '//*[@id="js_content"]/section[19]/section[2]/p//text()'
    datainfo = open(r'/srv/shixun/static/爬取高校警情数据.csv', mode='w+', encoding='utf-8', newline='')
    csv_writer = csv.DictWriter(datainfo, fieldnames=['诈骗信息', '文章发布时间'])
    # 设置表头
    csv_writer.writeheader()
    # 爬出最新部分的数据
    for index, row in differce_info.iterrows():
        link = row['文章地址']
        response = requests.get(link)
        print(response)
        root = etree.HTML(response.text)
        tempStr = ''
        update_time = row['文章发布时间']
        section = root.xpath(XpathV1)
        if section == []:
            section = root.xpath(XpathV2)
        if section == []:
            section = root.xpath(XpathV3)
        if section == []:
            section = root.xpath(Xpath)
        print(section)
        for i in section:
            # tempStr作为临时变量存储列表中散乱的数据
            tempStr += i
            if str(i).endswith("。"):
                # 打包成字典写入
                dict = {
                    '诈骗信息': tempStr,
                    '文章发布时间': update_time
                }
                csv_writer.writerow(dict)
                print(dict)
                tempStr = ''
    datainfo.close()
    filedata = pd.read_csv(r'/srv/shixun/static/爬取高校警情数据.csv', encoding='utf8')
    return filedata


# # test
# url = 'https://mp.weixin.qq.com/cgi-bin/appmsg?action=list_ex&fakeid=MzA3MDU5MTMzMQ%3D%3D&query=&begin=0&count=4&type=9&need_author_name=1&token=1142341895&lang=zh_CN&f=json&ajax=1'
# cookie = 'RK=p5nM//k1Wy; ptcz=64002b001626fa09f9fd94549249e51bff1b40dbf63dfde6890b467ee25735bd; eas_sid=j1p6d5T4C6b886u6p9x7S4t8V0; o_cookie=1787899331; pac_uid=1_1787899331; tvfe_boss_uuid=09ed4fe0ebe3f6ba; LW_uid=R1t64548d560o2V2l3J1q9X0x1; ied_qq=o1787899331; fqm_pvqid=b322ce03-a7e0-4950-8873-9a1028691317; clickNums=1; uin_cookie=o2023858186; LW_sid=C116n6W5X0S9k8R72181J1Y709; pgv_pvid=364990372; ua_id=yu9q5dB6SaFhete8AAAAAOcdy4WBPRnZSVSgnu1S3n8=; wxuin=66150082002754; mm_lang=zh_CN; rand_info=CAESIAnQwQSUxaNxQLLaCdug78vFaG38Iql1LHs8X/aBsgV9; slave_bizuin=3921418942; data_bizuin=3921418942; bizuin=3921418942; data_ticket=dziDWMUb1tS9FLQ6UnkismUzRt7MOXjjB8horOZyCnBQBpR/bVQQUOUxVR2X8chE; slave_sid=Sk9BSlBSZWNJeUY0d2lNa2VSWUNFT3ozWHFYUVFhQ2xOUnZqSkdmYm5kclBvVVhBR2lmX1lSQldSdFdaM2EwSGVxVTA1R1VMRnViV3NsaHQxaFFiYmc1dXhMbHpKTm1zMW93QVd1clZsVTI2Q1JxQVlpTzZZREJ4NmJ2UktjR3d6N2Q1VlAwdHF4cHVJdmNU; slave_user=gh_0c120afeafa0; xid=9dbee6db934a9eb56f1b6df567a30c58; _clck=3921418942|1|f7c|0'
# referer = 'https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=0&token=1142341895&lang=zh_CN'
# data = infoHandler(cookie, referer, url)
# print(data)


def filter4data(df, conn):
    # 创建数据库对象
    cursor = conn.cursor()

    # 创建总表
    sql = 'create table if not exists 诈骗数据 (id int NOT NULL AUTO_INCREMENT, schoolName varchar(255),' \
          ' fraudWay varchar(255), money int, month varchar(255), time varchar(255), PRIMARY KEY (`id`))'
    sql4truncatetemptable = 'truncate table anitifruad_temp'
    sql4data2antifruadtemptable = 'INSERT INTO anitifruad_temp (schoolName, fraudWay, money, month, time) VALUES (%s,%s,%s,%s,%s)'
    sql3 = 'INSERT INTO 诈骗数据 (schoolName, fraudWay, money, month, time) VALUES (%s,%s,%s,%s,%s)'
    cursor.execute(sql)


    file = open(r'/srv/shixun/static/诈骗数据.csv', 'w+', encoding='utf-8', newline='')
    spamwriter = csv.DictWriter(file, fieldnames=['高校名称', '诈骗方式', '诈骗金额', '诈骗月份', '文章发布时间'])
    spamwriter.writeheader()
    # 删去上次更新时存入的临时表数据
    cursor.execute(sql4truncatetemptable)
    for index, row in df.iterrows():
        time = row['文章发布时间']
        temp = re.split('-', time)
        month = temp[1] + '月'
        tempStr = row['诈骗信息']
        # 把字符串格式化为相同格式
        ret = re.sub('[人民币]', '', tempStr)
        # 从字符串中分隔出学校，诈骗方式，金额，时间。
        ret = re.split('[一]|“|”|[诈骗]|[元]', ret)
        money = ret[-2]
        if ' ' in ret[0]:
            ret[0] = ret[0].replace(' ', '')
        if '校区' in ret[0]:
            ret[0] = re.sub(r'[\u4e00-\u9fa5]{2}校区', '', ret[0])
        if '学校' in ret[0]:
            ret[0] = ret[0].replace('学校', '学院')
        if '大学' not in ret[0]:
            if '学院' not in ret[0]:
                ret[0] = ret[0].replace('学', '学院')
        if '司法学院' in ret[0]:
            ret[0] = ret[0].replace('司法学院', '司法警官学院')
        if '工程学院' in ret[0]:
            if '生态工程学院' in ret[0]:
                ret[0] = ret[0].replace('生态工程学院', '生态工程职业学院')
            if '技术工程学院' in ret[0]:
                ret[0] = ret[0].replace('技术工程学院', '工程职业技术学院')
            if '工程学院' in ret[0]:
                ret[0] = ret[0].replace('工程学院', '工程职业技术学院')
        if '技术职业学院' in ret[0]:
            ret[0] = ret[0].replace('技术职业学院', '职业技术学院')
        if '技术学院' in ret[0]:
            if '职业技术学院' not in ret[0]:
                ret[0] = ret[0].replace('技术学院', '职业技术学院')
        if '职业学院' in ret[0]:
            if '生态工程职业学院' not in ret[0]:
                ret[0] = ret[0].replace('职业学院', '职业技术学院')
        if '广东省' in ret[0]:
            ret[0] = ret[0].replace('广东省', '广东')
        if '广东岭南职业技术学院' in ret[0]:
            ret[0] = ret[0].replace('广东', '')
        if '万' in ret[-1]:
            temp = ret[-1].replace('万。', '')
            temp1 = float(temp)
            temp2 = temp1 * 10000
            temp2 = "{:.0f}".format(temp2)
            temp3 = str(temp2)
            money = temp3
        if '万' in money:
            temp = money.replace('万', '')
            temp1 = float(temp)
            temp2 = temp1 * 10000
            temp2 = "{:.0f}".format(temp2)
            temp3 = str(temp2)
            money = temp3
        dit = {
            '高校名称': ret[0],
            '诈骗方式': ret[2],
            '诈骗金额': money,
            '诈骗月份': month,
            '文章发布时间': time
        }
        # 执行插入表数据语句
        cursor.execute(sql3, (ret[0], ret[2], money, month, time))
        cursor.execute(sql4data2antifruadtemptable, (ret[0], ret[2], money, month, time))
        spamwriter.writerow(dit)
        conn.commit()
    file.close()
    conn.close()


# 更新操作
def update4table(conn):
    cursor = conn.cursor()
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
    #
    conn.commit()
    conn.close()
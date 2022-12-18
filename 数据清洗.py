import csv
import re
# 操作文件对象时，需要添加newline参数逐行写入，否则会出现空行现象
# delimiter 指定分隔符，默认为逗号
# quotechar 表示引用符
# writerow 单行写入，列表格式传入数据

with open(r'/srv/shixun/static/爬取高校警情数据.csv', 'r', newline='', encoding='utf-8')as csvfile:
    with open(r'/srv/shixun/static/诈骗数据.csv', 'w', encoding='utf-8', newline='') as f:
        spamwriter = csv.DictWriter(f, fieldnames=['高校名称', '诈骗方式', '诈骗金额', '诈骗月份', '文章发布时间'])
        spamreader = csv.DictReader(csvfile)
        spamwriter.writeheader()
        tempStr = ''
        ret = ''
        time = ''
        for row in spamreader:
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
                temp2 = temp1*10000
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
            spamwriter.writerow(dit)

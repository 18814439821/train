import datetime
from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from sqlalchemy import func
from padef import infoHandler, filter4data, update4table
import os
from functools import wraps
import base64

app = Flask(__name__)

# MySQL所在的主机名
HOSTNAME = "127.0.0.1"
# MySQL监听的端口号，默认3306
PORT = 3306
# 链接MySQL的用户名
USERNAME = "root"
# 链接mysql的密码
PASSWORD = ""
# MySQL上创建的数据库名称
DATABASE = "echarts"

app.config[
    'SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DATABASE}?charset=utf8"

# 在app.config中设置好链接数据库的信息
# 使用SQLAlchemy(app)创建一个db对象
# SQLAlchemy会自动读取app.config中链接数据库的信息

db = SQLAlchemy(app)


def generate_secret_key():
    return base64.b64encode(os.urandom(32)).decode('utf-8')


app.secret_key = generate_secret_key()


# user
class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))


# 学校名称 案件次数 累计金额
class UnivCount(db.Model):
    __tablename__ = "univcount"
    univName = db.Column(db.String(255), primary_key=True)
    count = db.Column(db.Integer)
    money = db.Column(db.Integer)


# 发生月份 月份诈骗金额
class MonthMoney(db.Model):
    __tablename__ = "monthmoney"
    month = db.Column(db.String(255), primary_key=True)
    money = db.Column(db.Integer)
    count = db.Column(db.Integer)


# 案件类型 发生次数 金额
class FraudWayCount(db.Model):
    __tablename__ = "fraudwaycount"
    fraudway = db.Column(db.String(255), primary_key=True)
    count = db.Column(db.Integer)
    money = db.Column(db.Integer)


# 按月份查询 案件类型 发生次数
class FraudData(db.Model):
    __tablename__ = '诈骗数据'
    id = db.Column(db.Integer, primary_key=True)
    schoolName = db.Column(db.String(255))
    fraudWay = db.Column(db.String(255))
    month = db.Column(db.String(255))
    money = db.Column(db.Integer)
    time = db.Column(db.String(255))


# 临时表
class FraudDataTemp(db.Model):
    __tablename__ = 'anitifruad_temp'
    id = db.Column(db.Integer, primary_key=True)
    schoolName = db.Column(db.String(255))
    fraudWay = db.Column(db.String(255))
    month = db.Column(db.String(255))
    money = db.Column(db.Integer)
    time = db.Column(db.String(255))


# 副页总表
class AllData(db.Model):
    __tablename__ = 'alldata'
    data = db.Column(db.String(255), primary_key=True)


@app.route("/")
def query_datas():
    # 查新增表
    tempdata = FraudDataTemp.query.all()
    # 查最后更新时间 并比较
    timedata = db.session.query(FraudData.time).all()
    lasttime = datetime.datetime.strptime("2022-01-01 0:0:0", "%Y-%m-%d %H:%M:%S")
    for time in timedata:
        temptime = datetime.datetime.strptime(time[0], "%Y-%m-%d %H:%M:%S")
        if temptime > lasttime:
            lasttime = temptime
    lasttime = lasttime.strftime("%Y-%m-%d %H:%M:%S")

    # 柱状图 图表所需数据
    univName = []  # 学校名称
    count = []  # 案件发生次数
    univName_copy = []  # 学校名称
    count_copy = []  # 案件发生次数
    data1 = UnivCount.query.order_by(UnivCount.count.desc()).all()
    data1_copy = UnivCount.query.order_by(UnivCount.count.asc()).all()
    for data in data1:
        univName.append(data.univName)
        count.append(data.count)
    for data_copy in data1_copy:
        univName_copy.append(data_copy.univName)
        count_copy.append(data_copy.count)

    # 折线图 所需数据
    month = []  # 发生月份
    money = []  # 月份诈骗金额
    monthcount = []  # 该月案件发生次数
    data2 = MonthMoney.query.all()
    for data_line in data2:
        month.append(data_line.month)
        money.append(data_line.money)
        monthcount.append(data_line.count)

    # top5 所需数据
    fraudway = []  # 案件名称
    top5count = []  # 每种案件发生次数
    data3 = FraudWayCount.query.order_by(FraudWayCount.count.desc()).limit(5).all()  # 取数据库案件类型次数最多的前5种

    for data_top5 in data3:
        fraudway.append(data_top5.fraudway)
        top5count.append(data_top5.count)
        # 因为饼图需要的数据是键值对 所以将列表转为dataFrame再转键值对
    df = pd.DataFrame({
        'name': fraudway,
        'value': top5count
    })
    top5_dict = df.to_dict(orient="records")  # top5的字典

    # top10排行榜
    names = []  # 学校名称
    schoolMoney = []  # 各个学校所被骗金额
    data4 = UnivCount.query.order_by(UnivCount.money.desc()).limit(10).all()  # 取数据库金额前10的数据
    for data_top10 in data4:
        names.append(data_top10.univName)
        schoolMoney.append(data_top10.money)

    # 求百分比 100%为金额最高的学校 其余学校去除第一名的学校后乘百分比
    j = 0
    for i in schoolMoney:
        if i > j:
            j = i
    num = []
    for i in schoolMoney:
        x = (round(i / j, 2)) * 100
        num.append(x)

    # 查询数据表一共有多少种案件类型  中间的环形图所需数据
    fraudwaySum = db.session.query(FraudWayCount.fraudway).count()  # 查询出数据库中所有的案件类型
    first = 0  # 定义外边的图一共有多少种类型
    second = 0  # 定义内边的图一共有多少类型
    if fraudwaySum % 2 == 0:
        first = second = fraudwaySum // 2
    else:
        first = (fraudwaySum // 2) + 1
        second = fraudwaySum // 2

    # 案件类型 发生次数 金额 前十条 假设20种类型 21种就是 前11条
    fraudway2 = []  # 案件类型
    moneycount = []  # 每种案件对应的被骗金额
    fraudways = []  # 记录案件类型名称 来制作前端图例
    data5 = FraudWayCount.query.order_by(FraudWayCount.money.desc()).limit(first).all()
    for firstdata in data5:
        fraudway2.append(firstdata.fraudway)
        moneycount.append(firstdata.money)
        fraudways.append(firstdata.fraudway)
    df2 = pd.DataFrame({
        'name': fraudway2,
        'value': moneycount
    })
    first_dict = df2.to_dict(orient="records")  # 外环的字典

    # 案件类型 发生次数 金额 后十条 假设20种类型
    fraudway3 = []  # 案件类型
    moneycount2 = []  # 金额
    data6 = FraudWayCount.query.order_by(FraudWayCount.money.asc()).limit(second).all()  # 查出内环数据
    for seconddata in data6:
        fraudway3.append(seconddata.fraudway)
        moneycount2.append(seconddata.money)
        fraudways.append(seconddata.fraudway)
    df3 = pd.DataFrame({
        'name': fraudway3,
        'value': moneycount2
    })
    second_dict = df3.to_dict(orient="records")  # 内环字典

    # hide隐藏框
    today = datetime.datetime.today()
    nowmonth = today.month
    if (nowmonth > 9):
        newmonth = str(nowmonth) + '月'
    else:
        newmonth = '0' + str(nowmonth) + '月'

    monthfraudcount = 0  # 本月发生案件
    moneyfraudcount = 0  # 本月累计诈骗金额
    hidefraud = []  # 案件类型
    hidecount = []  # 案件发生次数
    hidemoney = []  # 案件类型对应的金额
    data7 = db.session.query(FraudData.fraudWay, func.count(FraudData.fraudWay), FraudData.money).filter_by(
        month=newmonth).group_by(
        FraudData.fraudWay).order_by(func.count(FraudData.fraudWay).desc()).all()
    for hdata in data7:
        hidefraud.append(hdata.fraudWay)
        hidecount.append(hdata[1])
        monthfraudcount += hdata[1]
        moneyfraudcount += hdata.money
        hidemoney.append(hdata.money)
    df4 = pd.DataFrame({
        'name': hidefraud,
        'value': hidemoney
    })
    hide_dict = df4.to_dict(orient="records")

    return render_template("index.html",
                           count=count, univName=univName, univName_copy=univName_copy, count_copy=count_copy,  # 柱状图数据
                           month=month, money=money, monthcount=monthcount,  # 折线图数据
                           top5_dict=top5_dict,  # top5数据
                           schoolMoney=schoolMoney, names=names, num=num,  # top10数据
                           first_dict=first_dict, second_dict=second_dict, fraudways=fraudways, first=first, second=second,  # 所有案件类型的环形图
                           hidefraud=hidefraud, hidecount=hidecount, monthfraudcount=monthfraudcount,  # 隐藏柱状图
                           moneyfraudcount=moneyfraudcount, hide_dict=hide_dict,  # 隐藏饼图
                           lasttime=lasttime, tempdata=tempdata
                           )


@app.route('/update', methods=['POST'])
def update():
    cookies = request.form['cookies']
    url = request.form['url']
    referer = request.form['referer']
    print(cookies)
    print(referer)
    print(url)
    pageinfo = infoHandler(cookies=cookies, referer=referer, url=url)
    filter4data(pageinfo, db.engine.connect().connection)
    update4table(db.engine.connect().connection)
    return redirect("/")


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        print(session)
        if 'user_id' not in session:
            print("未登陆")
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)

    return wrapper


@app.route("/admin")
@login_required
def admin():
    return render_template("chartManagePage.html")


@app.route("/alldata")
def query_datas1():
    # 查询副页总表
    alldata = AllData.query.all()

    timedata = db.session.query(FraudData.time).all()
    lasttime = datetime.datetime.strptime("2022-01-01 0:0:0", "%Y-%m-%d %H:%M:%S")
    for time in timedata:
        temptime = datetime.datetime.strptime(time[0], "%Y-%m-%d %H:%M:%S")
        if temptime > lasttime:
            lasttime = temptime
    lasttime = lasttime.strftime("%Y-%m-%d %H:%M:%S")

    return render_template("showAll.html", alldata=alldata, lasttime=lasttime)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # 如果是 POST 请求，则验证用户名和密码
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 从数据库中查询用户信息
        user = User.query.filter_by(username=username).first()
        print(user)
        if user is None or user.password != password:
            # 用户名或密码错误，显示错误消息
            errMsg = "账号或密码错误"
            return render_template('login.html', errMsg=errMsg)

        # 用户名和密码正确，将用户 ID 写入 cookies
        session['user_id'] = user.id
        return redirect('/admin')
    # 如果是 GET 请求，则显示登录表单
    if request.method == 'GET':
        return render_template("login.html")


if __name__ == '__main__':
    app.run(host='0.0.0.0')

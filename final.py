import tkinter
from bs4 import BeautifulSoup
import  requests
import threading
import queue
import time
import random
import pymysql
import numpy as np
import matplotlib.pyplot as plt


lock=threading.Lock()
conn=pymysql.connect("localhost","root","","py",8806)
cursor = conn.cursor()
cnt=0
myqueue=queue.Queue()
areaset=[]
plt.rcParams['font.sans-serif']=['SimHei'] #用来正常显示中文标签
plt.rcParams['axes.unicode_minus']=False #用来正常显示负号
r=0; var1=0; var2=0; var3=0;weather=0;
class pro(threading.Thread):
    def __init__(self,url,area):
        threading.Thread.__init__(self)
        self.url=url
        self.area=area
    def run(self):
        page = requests.session().get(self.url)
        soup = BeautifulSoup(page.text.encode('ISO-8859-1'), 'lxml')
        div = soup.find("div", class_="conMidtab")
        for td in div.find_all('td', attrs={"height": "23", "width": "83"}):
            a = td.find('a')
            getcity(a["href"],self.area,a.string)


def getcity(url,area,city):
    page = requests.session().get(url)
    soup = BeautifulSoup(page.text.encode('ISO-8859-1'), 'lxml')
    i= soup.find('li', class_='sky')
    ti=i.find("h1").string
    wea=i.find("p",class_="wea").string
    Tem=""
    tem=i.find("p",class_="tem")
    temspan=tem.find("span")
    temi=tem.find("i")
    if(temspan!=None):
        Tem+=temspan.string+" "
        Tem+=temi.string
        av_tem=int((int(temspan.string)+int(temi.string[0:-1]))/2)
    else :
        Tem=temi.string
        av_tem=int(temi.string[0:-1])
    win=i.find("p",class_="win")
    winem=win.find("em")
    winemspan=winem.find_all("span")
    Wind=''
    for j in winemspan:
        Wind+=j['title']
        Wind+=" "
    Wind+=win.find("i").string
    ss=area+"  "+city+"   "+ti+"  "+wea+"  "+Tem+"  "+str(av_tem)+"  "+Wind
    sql="insert into w values('%s','%s','%s','%s','%s',%s,'%s') " %(area,city,ti,wea,Tem,av_tem,Wind)
    global cnt
    cnt+=1
    lock.acquire()
    cursor.execute(sql)
    lock.release()
    print(sql)


#
# class con(threading.Thread):
#     def __init__(self, name, size):
#         threading.Thread.__init__(self, name=name)
#         self.size = size
#
#     def run(self):
#         for i in range(self.size):
#             ans = myqueue.get()
#             print("消费" + ans)
#             weather.insert(tkinter.END, ans)
#             time.sleep(random.randint(1, 3))



class solve(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.start()
    def run(self):
        global cnt,areaset
        cnt=0
        t1=time.time()
        with open("log.txt", "w") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())+"\n")
        cursor.execute("delete from w")

        plist = []
        if (var1.get() == 1):
            url="http://www.weather.com.cn/textFC/hb.shtml"
            p1=pro(url,"华北")
            p1.daemon = True
            plist.append(p1)
            areaset.append("华北")
        if (var2.get() == 1):
            url = "http://www.weather.com.cn/textFC/db.shtml"
            p2=pro(url,"东北")
            p2.daemon = True
            plist.append(p2)
            areaset.append("东北")
        if (var3.get() == 1):
            url = "http://www.weather.com.cn/textFC/hd.shtml"
            p3 = pro(url,"华东")
            p3.daemon = True
            plist.append(p3)
            areaset.append("华东")
        # consumer = con("consumer", len(plist))
        for i in plist:
            i.start()
        num=len(threading.enumerate())
        # consumer.start()
        for i in plist:
            i.join()
        # consumer.join()
        print("结束----------------------------")
        t2=time.time()
        with open("log.txt", "a") as f:
            f.write("运行"+str(t2-t1)+"秒  "+"用了"+str(num)+"个线程 "+"爬取"+str(cnt)+"条数据 "+time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def gethist():
    global areaset
    sql = "select area,avg(av_tem) from w group by area"
    cursor.execute(sql)
    results = cursor.fetchall()
    for row in results:
        ss = row[0] + "的平均温度为" + str(row[1])
        weather.insert(tkinter.END, ss)
    xsum=[]
    for area in areaset:
        sql='select av_tem from w where area="%s"' %(area)
        x=[]
        cursor.execute(sql)
        results=cursor.fetchall()
        for row in results:
            x.append(row[0])
        xsum.append(x)
    plt.hist(xsum,label=areaset)
    plt.legend()
    plt.xlabel('温度')
    plt.ylabel('个数')
    plt.title("地区温度表")
    plt.show()

def getpie():
    global areaset
    i=1
    plt.title("各地区温度的饼状图")
    for area in areaset:
        x=[]
        labels=['20度以下','20-25度','26-30度','30度以上']
        sql='select count(*) from w where av_tem<20 and area="%s" ' %(area)
        cursor.execute(sql)
        results=cursor.fetchall()
        for row in results:
            x.append(row[0])
        sql = 'select count(*) from w where av_tem>=20 and av_tem<=25 and area="%s" ' % (area)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            x.append(row[0])
        sql = 'select count(*) from w where av_tem>=26 and av_tem<=30 and area="%s" ' % (area)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            x.append(row[0])
        sql = 'select count(*) from w where av_tem>30 and area="%s" ' % (area)
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            x.append(row[0])
        plt.subplot(1,3,i); i+=1
        plt.title(area)
        plt.pie(x,labels=labels,autopct='%.0f%%')

    plt.show()


def getboxplot():
    global areaset
    xsum=[]
    for area in areaset:
        sql='select av_tem from w where area="%s"' %(area)
        cursor.execute(sql)
        results=cursor.fetchall()
        x=[]
        for row in results:
           x.append(row[0])
        xsum.append(x)
    plt.boxplot(xsum,labels=areaset,sym="o")
    plt.show()








if __name__=="__main__":
    root = tkinter.Tk()
    varName = tkinter.StringVar()
    varName.set('')
    varPwd = tkinter.StringVar()
    varPwd.set('')
    # 创建标签
    labelName = tkinter.Label(root, text='用户名:', justify=tkinter.RIGHT, width=80)
    # 将标签放到窗口上
    labelName.place(x=10, y=5, width=80, height=20)
    # 创建文本框，同时设置关联的变量
    entryName = tkinter.Entry(root, width=80, textvariable=varName)
    entryName.place(x=100, y=5, width=80, height=20)

    labelPwd = tkinter.Label(root, text='密码:', justify=tkinter.RIGHT, width=80)
    labelPwd.place(x=10, y=30, width=80, height=20)
    # 创建密码文本框
    entryPwd = tkinter.Entry(root, show='*', width=80, textvariable=varPwd)
    entryPwd.place(x=100, y=30, width=80, height=20)


    # 登录按钮事件处理函数
    def login():
        # 获取用户名和密码
        name = entryName.get()
        pwd = entryPwd.get()

        conn = pymysql.connect('localhost', 'root', '', 'py', 8806)
        cursor = conn.cursor()
        sql = "select * from user where u='%s' and p='%s'" % (name, pwd)
        print(sql)
        cursor.execute(sql)
        if (cursor.rowcount >= 1):
            root.destroy()
            global r,var1,var2,var3,weather
            r = tkinter.Tk()
            r['height'] = 500
            r['width'] = 500
            var1 = tkinter.IntVar()
            var2 = tkinter.IntVar()
            var3 = tkinter.IntVar()
            tkinter.Checkbutton(r, text="华北", variable=var1).place(x=0, y=5)
            tkinter.Checkbutton(r, text="东北", variable=var2).place(x=100, y=5)
            tkinter.Checkbutton(r, text="华东", variable=var3).place(x=200, y=5)
            tkinter.Button(r, text="开始爬取", command=solve).place(x=200, y=30)
            tkinter.Button(r, text="直方图", command=gethist).place(x=270, y=30)
            tkinter.Button(r, text="饼状图", command=getpie).place(x=320, y=30)
            tkinter.Button(r, text="箱线图", command=getboxplot).place(x=370, y=30)
            weather = tkinter.Listbox(r)
            weather.place(x=0, y=100, width=450)
            r.mainloop()
        else:
            tkinter.messagebox.showerror('Python tkinter', message='Error')


    # 创建按钮组件，同时设置按钮事件处理函数
    buttonOk = tkinter.Button(root, text='Login', command=login)
    buttonOk.place(x=30, y=70, width=50, height=20)


    # 取消按钮的事件处理函数
    def cancel():
        # 清空用户输入的用户名和密码
        varName.set('')
        varPwd.set('')


    buttonCancel = tkinter.Button(root, text='Cancel', command=cancel)
    buttonCancel.place(x=90, y=70, width=50, height=20)

    # 启动消息循环
    root.mainloop()


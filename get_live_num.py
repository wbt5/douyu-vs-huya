import requests
import sqlite3
import time
import schedule
from threading import Thread


class MyThread(Thread):

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.result = self.func()

    def get_result(self):
        return self.result


def get_tt(sec='%S'):
    tt = time.strftime("%Y-%m-%d %H:%M:{:s}".format(sec), time.localtime())
    return tt


def get_last_num():
    conn = sqlite3.connect('dy_vs_hy.db')
    cursor = conn.cursor()
    cursor.execute("SELECT douyu,huya FROM live_num WHERE id=(SELECT MAX(id) FROM live_num);")
    last_num = cursor.fetchone()
    cursor.close()
    conn.close()
    return last_num


def get_dy_live_num():
    while True:
        try:
            res_f = requests.get(url='https://www.douyu.com/gapi/rkc/directory/0_0/1', timeout=5).json()
            live_page = res_f.get('data').get('pgcnt')
            res_l = requests.get(url='https://www.douyu.com/gapi/rkc/directory/0_0/' + str(live_page), timeout=5).json()
            dy_live_num = (live_page - 1) * 120 + len(res_l.get('data').get('rl'))
            print(get_tt() + ' DOUYU DONE')
            return dy_live_num
        except requests.exceptions.RequestException:
            print(get_tt() + ' DOUYU HTTP ERROR AND RETRY')
        if time.localtime()[5] > 50:
            dy_live_num = get_last_num()[0]
            print(get_tt() + ' REPLACE WITH THE LAST DOUYU NUM')
            return dy_live_num


def get_hy_live_num():
    while True:
        try:
            res_f = requests.get(url='https://www.huya.com/cache.php?m=LiveList&page=1', timeout=5).json()
            hy_live_num = res_f.get('data').get('totalCount')
            print(get_tt() + ' HUYA DONE')
            return hy_live_num
        except requests.exceptions.RequestException:
            print(get_tt() + ' HUYA HTTP ERROR AND RETRY')
        if time.localtime()[5] > 50:
            hy_live_num = get_last_num()[1]
            print(get_tt() + ' REPLACE WITH THE LAST HUYA NUM')
            return hy_live_num


def get_live_num():
    tt = get_tt('00')
    print(tt + ' STARTING')
    t1 = MyThread(get_dy_live_num)
    t2 = MyThread(get_hy_live_num)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    dy_live_num = t1.get_result()
    hy_live_num = t2.get_result()
    conn = sqlite3.connect('dy_vs_hy.db')
    cursor = conn.cursor()
    sql = "INSERT INTO live_num(get_time,douyu,huya) VALUES('{}',{},{})".format(tt, dy_live_num, hy_live_num)
    cursor.execute(sql)
    conn.commit()
    cursor.close()
    conn.close()
    print(get_tt() + ' INSERT SUCCESS')


schedule.every().minute.at(":00").do(get_live_num)

while True:
    schedule.run_pending()
    time.sleep(1)

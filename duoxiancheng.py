#!/usr/bin/python3.6
# coding: utf-8
# 查询域名证书到期情况

import sys
import queue
import time
import string
import threading
import datetime
import re
import subprocess
from io import StringIO

exitFlag = 0

domain_list = []

fileinfo = sys.argv[1]

start = time.time()

def CreateList():
    f = open(fileinfo,'r')
    for line in f.readlines():
        domain_list.append(line.replace('\n', ''))
    return domain_list
    f.close()

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        process_data(self.name, self.q)

def process_data(threadName, q):
    while not exitFlag:
        #queueLock.acquire()
        if not workQueue.empty():
            a = q.get()
            f = StringIO()
            comm = f"curl -Ivs https://{a} --connect-timeout 10"
            result = subprocess.getstatusoutput(comm)
            f.write(result[1])
            m = re.search('expire date: (.*?)\n.*?', f.getvalue(), re.S)
            if m is None:
                    print("%-15s 访问失败 %s" %(a, threadName))
                    pass
            else:
                    expire_date = m.group(1)
                    b = re.sub(r'月', '', expire_date)
                    b = time.strptime(b, "%m %d %H:%M:%S %Y GMT")
                    expire_date = time.strftime("%Y-%m-%d", b)
                    print("%-15s CA过期时间: %s   %s" %(a, expire_date, threadName))
            #queueLock.release()
        else:
            #queueLock.release()
            pass

# 执行函数，生成列表
CreateList()

#threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5", "Thread-6", "Thread-7", "Thread-8", "Thread-9", "Thread-10", "Thread-11", "Thread-12"]
threadList = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20"]
#queueLock = threading.Lock()
workQueue = queue.Queue()
threads = []
threadID = 1

# 填充队列
#queueLock.acquire()
for word in domain_list:
    workQueue.put(word)
#queueLock.release()

# 创建新线程
for tName in threadList:
    thread = myThread(threadID, tName, workQueue)
    thread.start()
    threads.append(thread)
    threadID += 1

# 等待队列清空
while not workQueue.empty():
    pass

exitFlag = 1

for t in threads:
    t.join()
elapsed = (time.time() - start)
print("Time used:",elapsed)

#!/usr/bin/python3.6
# coding: utf-8

import re
import os
import sys
import time
import queue
import shutil
import string
import datetime
import threading
import subprocess
import multiprocessing
from io import StringIO
from multiprocessing import Pool
from multiprocessing import Process

exitFlag = 0
domain_list = []
fileinfo = sys.argv[1]
workQueue = multiprocessing.Manager().Queue()
start = time.time()


def CreateList():
    f = open(fileinfo, 'r')
    for line in f.readlines():
        domain_list.append(line.replace('\n', ''))
    return domain_list
    f.close()

def mk_localdir(file_name):
    if not os.path.isdir(file_name):
        os.mkdir(file_name)
    else:
        shutil.rmtree('file_name')
        os.mkdir('file_name')


def process_data(q):
    while not exitFlag:
        if not workQueue.empty():
            a = q.get()
            f = StringIO()
            comm = f"curl -Ivs https://{a} --connect-timeout 10"
            result = subprocess.getstatusoutput(comm)
            f.write(result[1])
            m = re.search('expire date: (.*?)\n.*?', f.getvalue(), re.S)
            if m is None:
                failed_domain = open('domain_passdate/failed_domain.txt', 'a', encoding='utf-8')
                failed_domain.write("%-15s 访问失败\n" % (a))
                failed_domain.close()
                #print("%-15s 访问失败" % (a))
                pass
            else:
                expire_date = m.group(1)
                b = re.sub(r'月', '', expire_date)
                b = time.strptime(b, "%m %d %H:%M:%S %Y GMT")
                expire_date = time.strftime("%Y-%m-%d", b)
                ma = expire_date[0:7]
                #print("%-15s CA过期时间: %s" % (a, expire_date))
                seccess_domain = open('domain_passdate' + '/' + ma, 'a', encoding='utf-8')
                seccess_domain.write("%-15s CA过期时间: %s\n" % (a, ma))
                seccess_domain.close()
        else:
            break


mk_localdir('domain_passdate')
CreateList()

for word in domain_list:
    workQueue.put(word)

p = Pool(80)
for i in range(80):
    p.apply_async(process_data, args=(workQueue,))
# 等待队列清空
# while not workQueue.empty():
#    pass
p.close()
p.join()
exitFlag = 1
elapsed = (time.time() - start)
print("Time used:", elapsed)

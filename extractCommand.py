#!/usr/bin/python26
#########################################################################
#   Name:           extractCommand.py                                   #
#   Version:        1.0                                                 #
#   Author:         xinyu7@staff.sina.com.cn                            #
#   Description:    extract Redis Commands from tcpdump file            #
#   Last update:    2013-03-22 14:29:30                                 #
#   Created:        2013-03-19 21:09:00                                 #
#########################################################################

import os
import sys
import re
import subprocess
from optparse import OptionParser 

def extractCommand(filename):
    file_object = open(filename)
    content_total = ""
    for line in file_object:
        if re.match(r'\d{2}:\d{2}:\d{2}',line):
            time_ip_result = line.split(' ')
            Time = time_ip_result[0]
            ClientIP = time_ip_result[2]
            if content_total:
                if re.search(r'\*\d+\.\.',content_total):
                    first = re.search(r'\*\d+\.\.',content_total).group()
                    index = content_total.index(first)
                    command_first = content_total[index:]
                    command_temp = re.sub(r'\*\d+\.\.','',command_first)
                    command_result = re.sub(r'\$\d+\.\.','',command_temp)
                    command = re.sub(r'\.\.',' ',command_result)
                    print "Time: %s ClientIP: %s -->Redis Command: %s" %(Time,ClientIP,command)
            content_total = ""
            continue
        content_list = line.split(" ")
        content = content_list.pop().rstrip('\n')
        content_total = content_total + content
                    
 
def tcpdump(eth,port,count):
    OUTPUT_FILE="./tcpdump_redis_%s.txt" %(port)
    if os.path.exists(OUTPUT_FILE):
        OUTPUT_FILE_BAK = "./tcpdump_redis_%s.txt.bak" %(port)
        os.rename(OUTPUT_FILE, OUTPUT_FILE_BAK)
    system_cmd = """ sudo tcpdump -i %s dst port %d -nn -s 0 -A -X -c %d > %s  """ %(eth,port,count,OUTPUT_FILE)
    pipe = subprocess.Popen(system_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True,stdin=subprocess.PIPE) 
    stdout, stderr = pipe.communicate()     
    return OUTPUT_FILE

def usage():
    print "Usage 1: extractCommand.py <-i eth*> <-p 86**> <-c count> |grep HGET|HGETALL ... * Please max(count) <100w, Or up to you !"; 
    print "Usage 2: extractCommand.py <-f filename(tcpdump)> |grep HGET|HGETALL|HSET ...."; 
    sys.exit(1)  

if __name__ == "__main__" :
    parser = OptionParser()
    parser.add_option("-p","--port",type="int",dest="port") 
    parser.add_option("-c","--count",type="int",dest="count") 
    parser.add_option("-i","--eth",type="string",dest="eth")
    parser.add_option("-f","--file",type="string",dest="filename")
    (options, agrgs) = parser.parse_args()
    try:
        if options.filename:
            filename = options.filename
            extractCommand(filename)
        else:
            if not options.port or not options.eth:
                usage()
            else:
                port = options.port
                eth = options.eth
                if options.count or options.count <1000:
                    count = 10000
                else:
                    count = options.count
                filename = tcpdump(eth,port,count)
                extractCommand(filename)
    except Exception,e:
        print str(e)
        sys.exit(1)


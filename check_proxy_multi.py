#!/usr/bin/env python3

import urllib3
from concurrent.futures import ThreadPoolExecutor
import sys, getopt

urls = [
        { 'expect': [200], 'url': 'http://en.wikipedia.org/wiki/2010-11_Premier_League-aa' },
#        { 'expect': [200], 'url': 'http://en.wikipedia.org/wiki/List_of_MythBusters_episodes' },
#        { 'expect': [200], 'url': 'http://en.wikipedia.org/wiki/List_of_Top_Gear_episodes' },
        { 'expect': [200], 'url': 'http://en.wikipedia.org/wiki/List_of_Unicode_characters' },
        { 'expect': [204], 'url': 'http://clients3.google.com/generate_204' },
        { 'expect': [200,302], 'url': 'http://www.google.fr/' },
        ]

# http://detectportal.firefox.com/canonical.html
# http://detectportal.firefox.com/success.txt?
# http://captive.apple.com/hotspot-detect.html
# http://www.msftconnecttest.com/connecttest.txt
# http://www.msftncsi.com/ncsi.txt

# http://www.openbsd.org/

# http://clients3.google.com/generate_204

status = { 'done': 0, 'ok': 0 }

def download(urlitem, cmanager):
    global status
    url = urlitem['url'] 
    expect = urlitem['expect']
    response = cmanager.request('GET', url)
    try:
        if response :
            status['done'] += 1
            if (response.status in expect):
                status['ok'] += 1
            #print("+++++++++  url: " + url)
            print("+++++++++ [%d/%d] url: %s" % (status['ok'], status['done'], url))
            print(response.data[:1024])
    except Exception as e:
        print(e)


def help(exitc=0):
    print ('test.py -i <inputfile> -o <outputfile>')
    sys.exit(exitc)

def main(argv):
    try:
        opts, args = getopt.getopt(argv,"hf:o:",["urlsfile=","ofile="])
    except getopt.GetoptError:
        help(2)
    for opt, arg in opts:
        if opt == '-h':
            help()
        elif (opt == '-f') or (opt == '--urlsfile'):
            print (arg)

    #connection_mgr = urllib3.PoolManager(maxsize=5)
    connection_mgr = urllib3.ProxyManager('http://10.5.1.86:3131/', maxsize=5)
    thread_pool = ThreadPoolExecutor(5)
    for urlitem in urls:
        thread_pool.submit(download, urlitem, connection_mgr)

    while True:
        print(status)

if __name__ == "__main__":
    main(sys.argv[1:])


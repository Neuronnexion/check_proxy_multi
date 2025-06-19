#!/usr/bin/env python3

import urllib3
from concurrent.futures import ThreadPoolExecutor
import sys, getopt, random, time
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

VERBOSE = False

status = { 'done': 0, 'ok': 0 }

def exitcode(level, msg):

    exits = {
        'O': { 'exit': 0, 'status': 'OK' },
        'C': { 'exit': 2, 'status': 'CRITICAL' },
        'U': { 'exit': 3, 'status': 'UNKOWN' },
        }

    if (not level in exits):
        print("Unknown exit level", level)
        sys.exit(-1)

    msgout = "check_proxy_multi %s - %s" % ( exits[level]['status'], msg )
    print (msgout)
    sys.exit(exits[level]['exit'])


def download(urlitem, cmanager):
    global status, VERBOSE

    url = urlitem['url'] 
    expect = urlitem['expect']
    response = cmanager.request('GET', url)
    try:
        if response :
            status['done'] += 1
            # print (type(response.status), response.status, type(expect), expect)
            if (response.status in expect):
                status['ok'] += 1
            #print("+++++++++  url: " + url)
            if ( VERBOSE ):
                print("+++++++++ [%d/%d] url: %s" % (status['ok'], status['done'], url))
                print(response.status, response.data[:1024])
    except Exception as e:
        print(e)

def load_urls(filename):
    global VERBOSE

    urls = []
    with open(filename) as fd:
        for l in fd.readlines():
            l = l.strip()
            # Format attendu :
            # 200,http://www.openbsd.org/
            # 200|204,http://clients3.google.com/generate_204
            # => code http 200 ou 204 
            # => url http://....
            ( expect, url ) = l.split(',')
            # we need "ints"
            expects = map (lambda x: int(x), expect.split('|'))
            url_data = { 'expect': expects, 'url': url }
            if ( VERBOSE ):
                print(expect, url)
            urls.append(url_data)

    return urls

def help(exitc=0, msg=None):
    # -I 10.5.8.13 -p 3131
    if ( msg is not None ):
        print (msg)
    print ('check_proxy_multi.py [-h] [-v] -I <proxy_ip> -p <proxy_port> -f <urls_file> [-n <number_of_checks>] [-t <timeout>]')
    sys.exit(exitc)

def main(argv):
    global VERBOSE

    try:
        opts, args = getopt.getopt(argv,"hvI:p:f:n:t:",["urlsfile=","nchecks=","timeout="])
    except getopt.GetoptError:
        help(2)

    urlsfile = None
    nchecks = 3
    timeout = 5
    proxy_ip = None
    proxy_port = None

    for opt, arg in opts:
        #print (opt, arg)
        if opt == '-h':
            help()
        elif opt == '-v':
            VERBOSE = True
        elif (opt == '-I'):
            proxy_ip = arg
        elif (opt == '-p'):
            proxy_port = arg
        elif (opt == '-f') or (opt == '--urlsfile'):
            #print (arg)
            urlsfile = arg
        elif (opt == '-n') or (opt == '--nchecks'):
            #print (arg)
            nchecks = int(arg)
        elif (opt == '-t') or (opt == '--timeout'):
            # print (opt, arg)
            timeout = int(arg)

    if ( urlsfile is None ):
        help(-1, "Missing file with list of urls to check")

    if ( proxy_ip is None ):
        help(-1, "Missing IP of proxy host")

    if ( proxy_port is None ):
        help(-1, "Missing port of proxy host")

    #connection_mgr = urllib3.PoolManager(maxsize=5)
    proxy_url = 'http://%s:%s/' % ( proxy_ip, proxy_port )

    #connection_mgr = urllib3.ProxyManager('http://10.5.1.86:3131/', maxsize=5)
    try:
        connection_mgr = urllib3.ProxyManager(proxy_url, maxsize=5)
        thread_pool = ThreadPoolExecutor(5)
    except Exception as e:
        print(e)
        exitcode ('U', 'Can not use proxy at %s' % proxy_url)

    try:
        urls = load_urls(urlsfile)
    except Exception as e:
        exitcode ('U', 'Can not open file %s' % urlsfile)

    # max is the number of url in list
    if ( nchecks > len(urls) ):
        nchecks = len(urls)

    # randomize url list, to take the nth first
    random.shuffle(urls)
    for urlitem in urls[0:nchecks]:
        thread_pool.submit(download, urlitem, connection_mgr)

    start_t = time.time()
    curr_t = time.time()
    while ( (status['done'] < nchecks) and ( curr_t < (start_t + timeout) ) ):
#    while True:
        #print((curr_t-start_t), timeout, status)
        time.sleep(0.01)
        curr_t = time.time()

    if ( status['ok'] > 0):
        # at least one success
        exitcode('O', '%(ok)d out of %(done)d URL have been opened successfuly' % status)
    elif ( (curr_t-start_t) > timeout ):
        exitcode('C', 'No URL has been opened successfuly within timeout (%d)' % timeout)
    else:
        # all failed
        exitcode('C', 'No URL has been opened successfuly')
        

if __name__ == "__main__":
    main(sys.argv[1:])


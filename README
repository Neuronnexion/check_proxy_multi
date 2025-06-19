
Nagios-like check plugin for proxy server with a url list

## What is it for ?

This was written as a check tool for proxy hosts begind a load-balancer.

The load-balancer executes the check every minute to know wether the proxy
backend is working correctly (can load websites) or not.

This was test with (old) zevent load-balancer. The check script is used as the
"farm guardian". 

The script loads URLs from a given file, take some of them (default 3), try to
(parallel) load them through given proxy settings. If at least one of them
loads correctly, it returns OK status. If all fail, it returns CRITICAL status.

## Usage

    check_proxy_multi.py [-h] [-v] -I <proxy_ip> -p <proxy_port> -f <urls_file> [-n <number_of_checks>] [-t <timeout>]

  * `proxy_ip` is the IP address of the backend to check.
  * `proxy_port` is the port of the proxy to check (often 3128, no default used)
  * `urls_file` is the file to load URLs from. Included `list_urls.txt` can be used.
  * `number_of_checks` is the number of parallel checks to run. Defaults to 3.
  * `timeout` is the maximum run time (seconds) for checks. If no URL is
    correctly loaded within this time, status is rturned as CRITICAL. Defaults
    to 5.

## URL file format

The URL lists use following format, one per line.

    <HTTP_CODES>,<URL>

  * `HTTP_CODES` is a pipe ( '|' ) separated list of HTTP return codes to match
    a "success". Usually 200, but 204 or 30x can be used. ( or whatever you
    expect as a success )
  * `URL` is the website URL

Thie repository contains `list_urls.txt` with common publicly accessible test site.


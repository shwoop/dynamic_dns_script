#!/usr/bin/python
# vim: set fileencoding=utf-8 :
'''
Dynamic DNS hack to keep home up to scratch.

A. Ferguson 09-11-2013

WTFPL licensed (http://www.wtfpl.net/txt/copying/)
'''

import sys, time, urllib, urllib2, datetime, socket

api_qry = {'domain' : 'bummedinthegob.co.uk',
           'password' : None,
           'command' : 'LIST'}

ipecho_urls = ['http://echoip.com',
                'http://ipecho.net/plain',
                'http://www.bummedinthegob.co.uk/ip_echo']

def url_request(values, url):
    ''' return array from url request passing dict of parameters. '''
    try:
        if values:
            data = urllib.urlencode(values)
            req = urllib2.Request(url, data)
            output = urllib2.urlopen(req)
        else:
            output = urllib2.urlopen(url)
        output = [x for x in output]
    except urllib2.HTTPError as e:
        print '%s : %s' % (e.code, e.reason)
    except urllib2.URLError as e:
        print 'URLError : %s' % (e.reason)
    except:
        print 'Unhandled Exception'
    
    output = output if output else None
    return output


def fetch_external_ip():
    ''' get WAN ip address '''
    response = None
    cnt = 0
    urlcnt = len(ipecho_urls)
    while not response:
        response = url_request(None, ipecho_urls[cnt%urlcnt])
        cnt += 1
    return response[0]


def fetch_dns_ip(url):
    ''' grab ip from dns record of hame subdomain. '''
    ipadd = socket.gethostbyname('hame.bummedinthegob.co.uk')
    output = ipadd if ipadd else None
    return output


def update_dns_record(command, url):
    l_qry = api_qry
    l_qry['command'] = command
    output = url_request(l_qry, url)
    return output


def main():
    ''' pull current DNS, fetch external ip, and update when required. '''

    if len(sys.argv) != 2:
        print 'DNS api password required as argument.'
        return -1

    ## general config
    API_URL = 'https://ctrlpanel.mythic-beasts.com/customer/primarydnsapi'
    API_REPLACE_T = 'REPLACE hame 3600 A %s'
    POLL_INTERVAL = 300     ## 300 seconds == 5 mins
    DNS_INTERVAL_LONG = datetime.timedelta(hours=4)
    DNS_INTERVAL_SHRT = datetime.timedelta(minutes=1)

    ## init
    api_qry['password'] = sys.argv[1]
    dns_next_poll = datetime.datetime.now() + DNS_INTERVAL_LONG
    true_ip = None
    dns_ip = None
    while not true_ip:
        true_ip = fetch_external_ip()
        time.sleep(5)
    while not dns_ip:
        dns_ip = fetch_dns_ip(API_URL)
        time.sleep(5)

    ## guts
    while True:
        dt = datetime.datetime.now()
        dts = str(dt)[:16]

        new_ip = fetch_external_ip()
        true_ip = new_ip if new_ip else true_ip

        if true_ip == dns_ip:
            if dt > dns_next_poll:
                new_ip = fetch_dns_ip(API_URL)
                if new_ip:
                    dns_ip = new_ip
                    interval = DNS_INTERVAL_LONG
                else:
                    interval = DNS_INTERVAL_SHRT
                dns_next_poll = dt + interval
            print 'STILL: %s: %s' % (true_ip, dts)

        else:
            ## update dns record and assume success but set short interval
            ## until next check.
            resp = update_dns_record(API_REPLACE_T % (true_ip), API_URL)
            dns_ip = true_ip
            dns_next_poll = dt + DNS_INTERVAL_SHRT
            print 'NOW: %s: %s' % (true_ip, dts)

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    main()

#!/usr/bin/python
# vim: set fileencoding=utf-8 :
'''

Dynamic DNS hack to keep home up to scratch.

A. Ferguson 09-11-2013

WTFPL licensed (http://www.wtfpl.net/txt/copying/)

'''

import sys, time, urllib, urllib2, datetime

api_qry = {'domain' : 'bummedinthegob.co.uk',
    'password' : None,
    'command' : 'LIST'}

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
        output = None
    except urllib2.URLError as e:
        print 'URLError : %s' % (e.reason)
        output = None
    except:
        print 'Unhandled Exception'
        output = None
    return output


def fetch_external_ip():
    ''' get WAN ip address '''
    ## bit of hack, should compile list and loop
    output = url_request(None, 'http://echoip.com')
    if not output:
        output = url_request(None, 'http://ipecho.net/plain')
        if not output:
            print 'can\'t find external ip'
    output = output[0] if output else None
    return output


def fetch_dns_ip(url):
    ''' grab ip from dns record of hame subdomain. '''
    output = url_request(api_qry, url)
    if output:
        output = [x.split()[3] for x in
                  output if x.startswith('hame')][0]
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
    POLL_INTERVAL = 300
    DNS_INTERVAL = datetime.timedelta(hours=4)

    ## init
    api_qry['password'] = sys.argv[1]
    dns_next_poll = datetime.datetime.now() + DNS_INTERVAL
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
                new_ip = fetch_dns_ip(values, API_URl)
                dns_ip = new_ip if new_ip else dns_ip
                dns_next_poll = dt + POLL_INTERVAL
            print 'STILL: %s: %s' % (true_ip, dts)

        else:
            resp = update_dns_record(API_REPLACE_T % (true_ip), API_URL)
            print resp
            time.sleep(10)
            new_ip = fetch_dns_ip(values, API_URL)
            dns_ip = new_ip if new_ip else dns_ip
            dns_next_poll = dt + POLL_INTERVAL
            print 'NOW: %s: %s' % (true_ip, dts)

        time.sleep(POLL_INTERVAL)


if __name__ == '__main__':
    ''' when run directly fire off main entry point. '''
    main()

#!/usr/bin/python
# vim: set fileencoding=utf-8 :
'''

Dynamic DNS hack to keep home up to scratch.

A. Ferguson 09-11-2013

WTFPL licensed (http://www.wtfpl.net/txt/copying/)

'''

import sys, time, urllib, urllib2, datetime

def fetch_external_ip():
    ''' get ip address '''
    try:
        output  = unicode(urllib2.urlopen(u'http://ipecho.net/plain').read())
    except:
        output = None
    return output

def fetch_dns_ip(values, api_url):
    ''' grab ip from dns record of hame subdomain. '''
    try:
        data = urllib.urlencode(values)
        req = urllib2.Request(api_url, data)
        response = urllib2.urlopen(req)
        output = [x.split()[3] for x in
                  response if x.startswith('hame')][0]
    except:
        output = None
    return output


def main():
    ''' pull current DNS, fetch external ip, and update when required. '''
    if len(sys.argv) != 2:
        print 'DNS api password required as argument.'
        return -1
    passwrd = sys.argv[1]
    
    ##  Config can go here because CBA
    api_url = 'https://ctrlpanel.mythic-beasts.com/customer/primarydnsapi'
    my_domain = 'bummedinthegob.co.uk'
    api_replace_t = 'REPLACE hame 3600 A {0}'
    api_list = 'LIST'
    time_out = 300 # seconds == 5 mins

    values = { 'domain' : my_domain,
               'password' : passwrd,
               'command' : api_list }

    while (True):
        true_ip = fetch_external_ip()
        dns_ip = fetch_dns_ip(values, api_url)

        if true_ip == dns_ip:
            print 'STILL: {0}: {1}'.format(
                    true_ip,
                    str(datetime.datetime.now()))
            time.sleep(time_out)
        else:
            v2 = values
            v2['command'] = api_replace_t.format(true_ip)
            data = urllib.urlencode(values)
            req = urllib2.Request(api_url, data)
            response = urllib2.urlopen(req)
            v2['command'] = api_list
            print 'NOW: {0}: {1}'.format(
                    true_ip,
                    str(datetime.datetime.now()))


if __name__ == '__main__':
    ''' when run directly fire off main entry point. '''
    main()

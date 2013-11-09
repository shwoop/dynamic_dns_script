#!/usr/bin/python
# vim: set fileencoding=utf-8 :
'''

Dynamic DNS hack to keep home up to scratch.

A. Ferguson 09-11-2013

WTFPL licensed (http://www.wtfpl.net/txt/copying/)

'''

import sys, re, urllib, urllib2

def fetch_external_ip():
    ''' get ip address '''
    try:
        ipecho  = unicode(urllib2.urlopen(u'http://ipecho.net/plain').read())
    except:
        ipecho = None
    return ipecho

def main():
    ''' pull current DNS, fetch external ip, and update when required. '''
    if len(sys.argv) != 2:
        print 'DNS api password required as argument.'
        return -1
    passwrd = sys.argv[1]
    
##  Config can go here because CBA
    ip_addy = '78.105.139.36'
    api_url = 'https://ctrlpanel.mythic-beasts.com/customer/primarydnsapi'
    my_domain = 'bummedinthegob.co.uk'
    api_command = 'REPLACE hame 3600 A {0}'.format(ip_addy)

    fucks = True
    while (fucks):

        ip = fetch_external_ip()
        print ip

        values = { 'domain' : my_domain,
                   'password' : passwrd,
                   'command' : api_command }

        data = urllib.urlencode(values)
        req = urllib2.Request(api_url, data)
        response = urllib2.urlopen(req)
        print response.read()

        fucks = None

    return 0

if __name__ == '__main__':
    ''' when run directly fire off main entry point. '''
    main()

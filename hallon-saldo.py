#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import html
import requests
import re
import sys
import logging
import config
import json

logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger('hallon-scrape')


class Hallon(object):
    """Handles connection to Hallon and extraction of subscription data"""
    def __init__(self, username, password):
        super(Hallon, self).__init__()
        self.username = username
        self.password = password

        self.start_url = 'https://www.hallon.se/logga-in'
        self.login_url = 'https://www.hallon.se/api/login/username'
        self.mypages_url = 'https://www.hallon.se/mina-sidor'

    def connect(self):
        with requests.Session() as s:
            r = s.get(self.start_url)
            reqvertoken = re.search(r'<.*token.*value=\"(.+)\"\s/>\s{3,}.*', r.text, re.I)
            logger.debug('Token is {0}'.format(reqvertoken.group(1)))
            headers = {
                'Content-Type': 'application/json',
                'VerificationToken': reqvertoken.group(1)
            }
            payload = {
                'username': self.username,
                'password': self.password,
                'rememberMe': False
            }
            s.post(self.login_url, data=json.dumps(payload), headers=headers)
            r = s.get(self.mypages_url)
        return r.content

    def _get_data(self):
        data = self.connect()
        return data

    def _format_output(self, subscription, phonenumber, elements):
        
        (callsmade, smssent, dataleft) = elements

        print('Nummer: {0} ({1})'.format(phonenumber, subscription))
        print('Saldo:')
        print(6 * '-')
        print('{} samtal gjorda'.format(callsmade))
        print('{} sms/mms skickade'.format(smssent))
        print('{} GB kvarvarande surf'.format(dataleft))

    def get_all_info(self):
        data = self._get_data()
        tree = html.fromstring(data)
        subscriptions = tree.xpath('//li[@class="myNumbers__list-item js-list-item"]')

        for subscription in subscriptions:
            phonenumber = subscription.xpath('.//span[@class="myNumbers__list-item-title-number"]/text()')[0]
            mypott = subscription.xpath('.//article[@class="myPott"]')
            for pott in mypott:
                subscriptionid = pott.attrib['data-filter']
                elems = pott.xpath('.//span[@class="amountused"]//text()')
            
            self._format_output(subscriptionid, phonenumber, elems)

    def get_info(self, phonenumber):
        data = self._get_data()
        tree = html.fromstring(data)
        try:
            subscription = tree.xpath('//*[.="{0}"]/../../..'.format(phonenumber))[0]
        except IndexError:
            print('{} kunde inte hittas.'.format(phonenumber))
            sys.exit(2)
        
        mypott = subscription.xpath('.//article[@class="myPott"]')
        for pott in mypott:
            subscriptionid = pott.attrib['data-filter']
            elems = pott.xpath('.//span[@class="amountused"]//text()')
        
        self._format_output(subscriptionid, phonenumber, elems)


def main():
    username = config.username
    password = config.password

    hallon = Hallon(username, password)

    if len(sys.argv) > 1:
        phonenumber = sys.argv[1]
        hallon.get_info(phonenumber)
    else:
        hallon.get_all_info()


if __name__ == '__main__':
    main()

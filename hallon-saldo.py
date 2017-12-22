#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lxml import html
import requests
import re
import sys
import logging
import config

logging.basicConfig(format='%(asctime)s %(levelname)s:%(name)s: %(message)s', level=logging.INFO)
logger = logging.getLogger('hallon-scrape')


class Hallon(object):
    """Handles connection to Hallon and extraction of subscription data"""
    def __init__(self, username, password):
        super(Hallon, self).__init__()
        self.username = username
        self.password = password

        self.login_url = 'https://www.hallon.se/logga-in'
        self.mypages_url = 'https://www.hallon.se/mina-sidor'

    def connect(self):
        with requests.Session() as s:
            r = s.get(self.login_url)
            reqvertoken = re.search(r'<.*token.*value=\"(.+)\"\s/>\s{3,}.*', r.text, re.I)
            logger.debug('Token is {0}'.format(reqvertoken.group(1)))
            payload = {
                'UserName': self.username,
                'Password': self.password,
                '__RequestVerificationToken': reqvertoken.group(1)
                }
            s.post(self.login_url, data=payload)
            r = s.get(self.mypages_url)
        return r.content

    def _get_data(self):
        data = self.connect()
        return data

    def _format_output(self, subscription, phonenumber, articles):
        formatted = []
        for article in articles:
            if article.startswith(' '):
                formatted.append(article + '\n')
            else:
                formatted.append(article)
        formatted.append(' GB data\n')
        print('Nummer: {0} ({1})'.format(phonenumber, subscription))
        print('Saldo:')
        print(6 * '-')
        print(''.join(formatted))

    def get_all_info(self):
        data = self._get_data()
        tree = html.fromstring(data)
        subscriptions = tree.xpath('//dd[@class="listitem"]')
        for subscription in subscriptions:
            ss = subscription.attrib['data-value']
            phonenumber = tree.xpath('//dd[@data-value="{0}"]/span[@class="phonenumber"]/text()'.format(ss))[0]
            articles = tree.xpath('//article[@class="whitebox myPott" and @data-filter="{0}"]/section/p//text() | //article[@class="whitebox myPott" and @data-filter="{0}"]/section/div/p//text()'.format(ss))
            self._format_output(ss, phonenumber, articles)

    def get_info(self, phonenumber):
        data = self._get_data()
        tree = html.fromstring(data)
        subscription = tree.xpath('//*[.="{0}"]/parent::dd'.format(phonenumber))[0]
        ss = subscription.attrib['data-value']
        articles = tree.xpath('//article[@class="whitebox myPott" and @data-filter="{0}"]/section/p//text() | //article[@class="whitebox myPott" and @data-filter="{0}"]/section/div/p//text()'.format(ss))
        self._format_output(ss, phonenumber, articles)


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

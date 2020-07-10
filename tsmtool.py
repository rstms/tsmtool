#!/usr/bin/env python
# tsmtool main module, cli 

import click
import requests
from bs4 import BeautifulSoup
from pprint import pprint
import json
import datetime

URL='https://www.tarsnap.com'

def _open_session(url, uid, key):
    s=requests.Session()
    #s.auth(uid, key)
    data={'address': uid, 'password': key}
    r=s.post(url, data)
    return s, r

def _round(value):
  return float('%.2f' % value)

@click.command()
@click.option('--uid', envvar='TSMTOOL_UID', help='account id for website login')
@click.option('--key', envvar='TSMTOOL_KEY', help='key (password) for website login')
@click.option('--rows', is_flag=True, help='include all row data')
@click.option('--balances', is_flag=True, help='include daily balances')
@click.option('--payments', is_flag=True, help='include payments')
@click.option('--raw', is_flag=True, help='raw day only (skip calculated fields)')
def cli(uid, key, rows, balances, payments, raw):

    if not uid:
        raise ValueError('--uid is required')
    if not key:
        raise ValueError('--key is required')
    s,r =_open_session(URL+'/manage.cgi', uid, key)
    soup = BeautifulSoup(r.text, 'html.parser')

    #for div in [soup.find('div')]:
    #   print('div: %s ' % repr(div.text))

    r={}
    for el in soup.find('div').find_all('p'):
        if 'current account balance' in el.text:
            r['balance'] = _round(float(el.find('code').text[1:]))
        elif 'logged in as' in el.text:
            r['account'] = el.find('code').text

    for el in soup.find_all('a', href=True):
        if el['href'].endswith('verboseactivity'):
            response = s.get('%s/%s' % (URL, el['href']))
            soup = BeautifulSoup(response.text, 'html.parser')
            break

    #print(soup.prettify())

    r['rows']=[]
    r['balances']=[]
    r['payments']={}
    payment_total = 0.0

    for el in soup.find('table').find_all('tr'):
        r['rows'].append([el.text for el in el.find_all('td') ])

    for row in r['rows']:
        if row[0]=='Balance':
            r['balances'].append((row[1], float(row[6])))
        if row[0]=='Payment':
            payment = float(row[5])
            r['payments'][row[1]]=payment
            payment_total += payment


    if not raw:
        begin_date = datetime.datetime.strptime(r['balances'][0][0], '%Y-%m-%d')
        begin_amount = float(r['balances'][0][1])
        end_date = datetime.datetime.strptime(r['balances'][-1][0], '%Y-%m-%d')
        end_amount = float(r['balances'][-1][1])
        r['monthly_cost'] = _round((begin_amount - (end_amount-payment_total)) / (end_date - begin_date).days * 365 / 12)

    if not rows:
       del(r['rows'])

    if not balances:
       del(r['balances'])

    if not payments:
       del(r['payments'])

    print(json.dumps(r))

if __name__ == '__main__':
    cli(auto_envvar_prefix='TSMTOOL')

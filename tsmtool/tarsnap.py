# Tarsnap - tarsnap website interface

import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.tarsnap.com"


class Tarsnap:
    def __init__(self, config_file, account, uid=None, key=None):

        self.url = URL
        self.uid = uid
        self.key = key
        self.account = account or "undefined"
        self.config = {}
        if config_file.exists():
            for line in Path(config_file).open("r").readlines():
                _account, _uid, _key = line.split()
                self.config[_account] = dict(uid=_uid, key=_key)

        _config = self.config.get(account, {})

        if account:
            self.uid = _config.get("uid")
            self.key = _config.get("key")

        self.session = requests.Session()

    def _post(self, route, data):
        return self.session.post(self.url + "/" + route, data)

    def _get(self, route):
        return self.session.get(self.url + "/" + route)

    def _round(self, value):
        return float("%.2f" % value)

    def _query(self):

        response = self._post(
            "manage.cgi", {"address": self.uid, "password": self.key}
        )

        # for div in [soup.find('div')]:
        #   print('div: %s ' % repr(div.text))

        balance = None
        account = None
        verbose_soup = None

        soup = BeautifulSoup(response.text, "html.parser")

        for el in soup.find("div").find_all("p"):
            if "current account balance" in el.text:
                balance = self._round(float(el.find("code").text[1:]))
            elif "logged in as" in el.text:
                account = el.find("code").text

        for el in soup.find_all("a", href=True):
            if el["href"].endswith("verboseactivity"):
                response = self._get(el["href"])
                verbose_soup = BeautifulSoup(response.text, "html.parser")
                break

        return balance, account, verbose_soup

    def _handle_row(self, r, row):
        if row[0] == "Balance":
            r["balances"].append((row[1], float(row[6])))
        if row[0] == "Payment":
            payment = float(row[5])
            r["payments"][row[1]] = payment
        else:
            payment = 0
        return payment

    def get_status(self, rows, balances, payments, raw, uid=None, key=None):

        uid = uid or self.uid
        key = key or self.key

        if not uid:
            raise ValueError("--uid is required")

        if not key:
            raise ValueError("--key is required")

        balance, account, soup = self._query()
        r = {}
        r["balance"] = balance
        r["account"] = account
        r["rows"] = []
        r["balances"] = []
        r["payments"] = {}
        payment_total = 0.0

        for el in soup.find("table").find_all("tr"):
            r["rows"].append([el.text for el in el.find_all("td")])

        for row in r["rows"]:
            payment_total += self._handle_row(r, row)

        if not raw:
            begin_date = datetime.datetime.strptime(
                r["balances"][0][0], "%Y-%m-%d"
            )
            begin_amount = float(r["balances"][0][1])
            end_date = datetime.datetime.strptime(
                r["balances"][-1][0], "%Y-%m-%d"
            )
            end_amount = float(r["balances"][-1][1])
            r["monthly_cost"] = self._round(
                (begin_amount - (end_amount - payment_total))
                / (end_date - begin_date).days
                * 365
                / 12
            )

        if not rows:
            del r["rows"]

        if not balances:
            del r["balances"]

        if not payments:
            del r["payments"]

        return r

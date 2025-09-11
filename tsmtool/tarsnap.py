# Tarsnap - tarsnap website interface

import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup, element

URL = "https://www.tarsnap.com"


class Tarsnap:
    def __init__(self, config_file, account=None, email=None, password=None):

        self.url = URL
        self.account = account or "undefined"
        self.config = {}
        if config_file and config_file.exists():
            for line in Path(config_file).open("r").readlines():
                _account, _email, _password = line.split()
                self.config[_account] = dict(email=_email, password=_password)
                if not account:
                    account = _account

        _config = self.config.get(account, {})

        self.email = email or _config.get("email")
        self.password = password or _config.get("password")

        self.session = requests.Session()

    def _post(self, route, data):
        return self.session.post(self.url + "/" + route, data)

    def _get(self, route):
        return self.session.get(self.url + "/" + route)

    def _round(self, value):
        return float("%.2f" % value)

    def _query(self):

        response = self._post("manage.cgi", {"address": self.email, "password": self.password})

        # for div in [soup.find('div')]:
        #   print('div: %s ' % repr(div.text))

        balance = None
        account = None
        verbose_soup = None

        soup = BeautifulSoup(response.text, "html.parser")
        # print(soup.prettify())

        for el in [e for e in soup.find_all("div") if e and isinstance(e, element.Tag)]:
            for div in [e for e in el.find_all("div") if e and isinstance(e, element.Tag)]:
                if div.attrs.get("class") == ["boxcontents"]:
                    msg = div.text.strip().split("\n")[0]
                    if f"You are logged in as {self.email}" not in msg:
                        raise RuntimeError(msg)

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
        payment_amount = 0
        if row[0] == "Balance":
            day_balance = float(row[6])
            r["balances"].append((row[1], day_balance))
            if self.last_balance != 0.0:
                daily_spend = self.last_balance - day_balance
                self.spends[row[1]] = daily_spend
            self.last_balance = day_balance
        elif row[0] == "Payment":
            payment_amount = float(row[5])
            self.last_balance += payment_amount
            r["payments"][row[1]] = payment_amount
        return payment_amount

    def get_status(
        self, rows=False, balances=False, payments=False, raw=False, email=None, password=None, last_payment=False, daily=False, days=0
    ):

        target_date = self.calculate_target_date(days)

        email = email or self.email
        password = password or self.password

        if not email:
            raise ValueError("--email is required")

        if not password:
            raise ValueError("--password is required")

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

        self.last_balance = 0.0
        self.spends = {}
        for row in r["rows"]:
            payment_total += self._handle_row(r, row)

        if not raw:
            daily_cost = sum(self.spends.values()) / len(self.spends)
            monthly_cost = daily_cost * 365.0 / 12.0
            if r["balances"]:
                r["monthly"] = monthly_cost
                if daily:
                    r["daily"] = daily_cost
                #monthly_cost = self.calculate_monthly_cost(r["balances"], payment_total)
                #r["daily"] = self._round(daily_cost)
                if days != 0:
                    r[target_date] = self._round(self.calculate_payment(balance, daily_cost, days))
                r["paid days"] = self.calculate_days(balance, daily_cost)

        if not rows:
            del r["rows"]

        if not balances:
            del r["balances"]

        if last_payment:
            r.update(self.last_payment_fields(r.get("payments", {})))
            payments = False

        if not payments:
            del r["payments"]

        return r

    def calculate_monthly_cost(self, balances, payment_total):
        begin_date = datetime.datetime.strptime(balances[0][0], "%Y-%m-%d")
        begin_amount = float(balances[0][1])
        end_date = datetime.datetime.strptime(balances[-1][0], "%Y-%m-%d")
        end_amount = float(balances[-1][1])
        return self._round((begin_amount - (end_amount - payment_total)) / (end_date - begin_date).days * 365 / 12)

    def last_payment_fields(self, payments):
        last_date = ""
        last_amount = ""
        if payments:
            last_date = sorted(list(payments.keys()))[-1]
            last_amount = payments[last_date]
        return dict(last_payment_date=last_date, last_payment_amount=last_amount)

    def calculate_days(self, balance, daily_cost): 
        days =  balance / daily_cost
        if days < 0:
            days -= 1
        return int(days)

    def calculate_payment(self, balance, daily_cost, days):
        if balance > daily_cost * days:
            return 0.0
        return float(int((daily_cost * days - balance) + 1))

    def calculate_target_date(self, days):
        target_date = datetime.datetime.today() + datetime.timedelta(days=days)
        return datetime.datetime.strftime(target_date, "%Y-%m-%d")
        


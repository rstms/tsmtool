from pathlib import Path

import pytest

from tsmtool import Tarsnap
from tsmtool.cli import DEFAULT_CONFIG


@pytest.fixture
def config_file():
    return Path(DEFAULT_CONFIG)


@pytest.fixture
def default_account(config_file):
    text = config_file.read_text()
    line = text.split("\n")[0]
    account = line.split()[0]
    return account


def test_tsmtool_report(config_file, default_account):
    t = Tarsnap(config_file, default_account)
    rows = True
    balance = True
    payments = True
    raw = False
    report = t.get_status(rows, balance, payments, raw)
    assert report
    assert isinstance(report, dict)

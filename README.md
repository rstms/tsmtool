=======
tsmtool
=======


![Image](https://img.shields.io/github/license/rstms/tsmtool)

![Image](https://img.shields.io/pypi/v/tsmtool.svg)


![Image](https://circleci.com/gh/rstms/tsmtool/tree/master.svg?style=shield)

![Image](https://readthedocs.org/projects/tsmtool/badge/?version=latest)

![Image](https://pyup.io/repos/github/rstms/tsmtool/shield.svg)

Tarsnap Status Monitor

The most excellent tarsnap.com has a clean and functional interface for managing one's account.  This tool connects to the
web interface and queries data, producing a JSON-formated report.  The current balance is read, and an estimated monthly
cost is calculated based on the site's daily cost data.

Here's an example of output from the author's account:
```
(tsmtool) mkrueger@beaker:~/src/tsmtool$ tsmtool rstms
{
  "balance": 32.51,
  "account": "mkrueger@rstms.net",
  "monthly_cost": 23.51
}
```

A config file may be used for account data, or the email account / password may be passed as command line options.
The config file is a whitespace delimited text file with one line per account.
Each line has these fields:

`~/.tsmtool`: 
```
ACCOUNT_NAME    EMAIL_ADDRESS   PASSWORD
```

* Free software: MIT license
* Documentation: https://tsmtool.readthedocs.io.



Credits
-------

This package was created with Cookiecutter and `rstms/cookiecutter-python-cli`, a fork of the `audreyr/cookiecutter-pypackage` project template.

[audreyr/cookiecutter](https://github.com/audreyr/cookiecutter)
[audreyr/cookiecutter-pypackage](https://github.com/audreyr/cookiecutter-pypackage)
[rstms/cookiecutter-python-cli](https://github.com/rstms/cookiecutter-python-cli)

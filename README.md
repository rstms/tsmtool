# tsmtool
Tarsnap Management Tool - scrapes usage data from tarsnap website and outputs in JSON

- assumes use of virtualenvwrapper 
- reads 1 or more lines of username, password data from `~/.tsmtool`

Installation example:
```
mkvirtualenv tsmtool
pip install .
deactivate
sudo cp bin/tarsnap-report /usr/local/bin
```


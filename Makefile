# make install, uninstall

.ONESHELL:
SHELL = /bin/bash

default:
	@echo "Commands:\n  make install\n  make uninstall"

.PHONY: install uninstall

venv:
	. `which virtualenvwrapper.sh`
	mkvirtualenv -p python3 tsmtool
	workon tsmtool

install:
	sudo pip install .
	sudo cp bin/tarsnap-report /usr/local/bin

uninstall:
	. `which virtualenvwrapper.sh`
	rmvirtualenv tsmtool
	sudo rm /usr/local/bin/tarsnap-report

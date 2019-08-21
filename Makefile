# make install, uninstall

.ONESHELL:
SHELL = /bin/bash

default:
	@echo "Commands:\n  make install\n  make uninstall"

.PHONY: install uninstall

install:
	. `which virtualenvwrapper.sh`
	mkvirtualenv -p python3 tsmtool
	pip install .
	deactivate
	sudo cp bin/tarsnap-report /usr/local/bin

uninstall:
	. `which virtualenvwrapper.sh`
	rmvirtualenv tsmtool
	sudo rm /usr/local/bin/tarsnap-report

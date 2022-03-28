# make clean targets

# generate Sphinx HTML documentation, including API docs
#
install-docs:
	pip install -U .[docs]

docs/readme.rst: README.md
	m2r2 --overwrite $<
	mv README.rst $@


docs: install-docs clean-docs docs/readme.rst
	sphinx-apidoc -o docs/ $(project)
	$(MAKE) -C docs html
	$(browser) docs/_build/html/index.html

# clean up documentation files
clean-docs:
	rm -f docs/$(project).rst
	rm -f docs/modules.rst
	rm -f docs/readme.rst
	$(MAKE) -C docs clean

# run a dev-mode docs webserver; recompiling on changes 
servedocs: docs
	watchmedo shell-command -p '*.rst' -c '$(MAKE) -C docs html' -R -D .

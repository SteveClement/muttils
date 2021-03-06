# $Id$

PREFIX=$(shell python -c "import sys; print sys.prefix")
export PREFIX
PYTHON=python
FIND=find

.PHONY: help all local build clean install install-home dist distclean

help:
	$(PYTHON) setup.py --description --version
	@echo
	@echo 'Commonly used make targets:'
	@echo '  all          - build programs'
	@echo '  install      - install programs to PREFIX ($(PREFIX))'
	@echo '  install-home - install with setup.py install --home=HOME ($(HOME))'
	@echo '  install-user - install with setup.py install --user'
	@echo '  local        - build for inplace usage'
	@echo '  clean        - remove files created by other targets'
	@echo '                 (except installed files or dist source tarball)'
	@echo
	@echo 'Example for a system-wide installation under $(PREFIX):'
	@echo '  make && sudo make install'
	@echo
	@echo 'Example for a local installation (usable in this directory):'
	@echo '  make local'

all: build

build:
	$(PYTHON) setup.py build

local:
	$(PYTHON) setup.py build_ext -i
	$(PYTHON) setup.py build_py -c -d .
	$(PYTHON) setup.py --description --version

clean:
	-$(PYTHON) setup.py clean --all # ignore errors of this command
	$(FIND) . -name '*.py[cdo]' -exec $(RM) '{}' ';'
	$(RM) MANIFEST muttils/__version__.py
	$(RM) -r build

install: build
	$(PYTHON) setup.py install --prefix="$(PREFIX)" --force
	$(PYTHON) setup.py --description --version

install-home: build
	$(PYTHON) setup.py install --home="$(HOME)" --force
	$(PYTHON) setup.py --description --version

install-user: build
	$(PYTHON) setup.py install --user --force
	$(PYTHON) setup.py --description --version

MANIFEST:
	$(PYTHON) setup.py --version
	$(PYTHON) setup.py sdist --manifest-only

dist:
	$(PYTHON) setup.py sdist

distclean: clean
	$(RM) -r dist

.DEFAULT_GOAL:= all

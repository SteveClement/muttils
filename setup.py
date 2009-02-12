#!/usr/bin/env python
# $Id$

import sys
if not hasattr(sys, 'version_info') or sys.version_info < (2, 4):
    raise SystemExit, 'Muttils requires Python 2.4 or later'

from distutils.core import setup
import subprocess, time

# specify version, Mercurial version otherwise
version = ''

if not version:
    try:
        v = subprocess.Popen(['hg', 'id', '-i', '-t'],
                             stdout=subprocess.PIPE).communicate()[0]
        v = v.split()
        while len(v) > 1 and v[-1][0].isalpha(): # no numbered tags
            v.pop()
        version = v[-1] or 'unknown'
        if version.endswith('+'):
            version += time.strftime('%Y%m%d')
    except OSError:
        version = 'unknown'

fp = file("muttils/__version__.py", "w")
fp.write('# this file is autogenerated by setup.py\n')
fp.write('version = "%s"\n' % version)
fp.close()

setup(name='muttils',
      version=version,
      description='Python utilities for console mail clients (eg. mutt)',
      author='Christian Ebert',
      author_email='blacktrash@gmx.net',
      url='http://www.blacktrash.org/hg/muttils/',
      packages=['muttils'],
      scripts=['sigpager', 'urlbatcher', 'urlpager',
               'pybrowser', 'wrap', 'viewhtmlmsg'])

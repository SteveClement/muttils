# $Id$

import urlregex.version
import os.path, re, sys

def fbox(s):
    '''Returns ascii-framed string s.'''
    frameline = '-' * (len(s) + 2)
    return ',' + frameline + '.\n| ' + s + ' |\n`' + frameline + "'"

def nlprepend(s):
    '''Returns string with newline prepended
    if not already present.'''
    return '\n'[s.startswith('\n'):] + s

class Usage(object):
    '''
    Provides generalized usage function.
    Help text (without executable name!) and
    version info may be initialized.
    '''
    def __init__(self, help=''):
        self.help = help

    def printhelp(self, err='', interrupt=False, **kwargs):
        '''Prepends name of current executable to every line
        of help text that does not start with a space.
        When no error is given, version info is printed when available.'''

        exe = os.path.basename(sys.argv[0])

        if self.help:
            help_re = re.compile(r'^(\S)', re.MULTILINE)
            msg = help_re.sub(r'%s \1' % exe, self.help)
            msg = 'Usage:' + nlprepend(msg)
        for kw in kwargs:
            msg += '\n%s:%s' % (kw, nlprepend(kwargs[kw]))

        if err:
            err = '%s: %s' % (exe, err)
            msg = fbox(err) + nlprepend(msg)
            if interrupt:
                sys.stderr.write('\n')
            sys.exit(msg)

        msg += '\n'
        rev = fbox('%s (version: %s)' % (exe, urlregex.version.getversion()))
        msg = rev + nlprepend(msg)
        sys.stdout.write(msg)
        sys.exit()
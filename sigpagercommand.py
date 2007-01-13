sigpager_cset = '$Id$'

### configure defaults manually:
# /path/to/dir/containing/sigfiles
signaturedir = '~/.Sig'
# common suffix of signature files
suffix = '.sig'
###

import getopt, sys
from tpager.sigpager import Signature, SignatureError

# d: sigdir, f [prepend separator], h [help],
# s: defaultsig, t: sigtail

sigpager_help = '''
[-d <sigdir>][-f][-s <defaultsig>] \\
         [-t <sigtail>][-]
[-d <sigdir>][-f][-s <defaultsig>] \\
         [-t <sigtail>] <file> [<file> ...]
-h (display this help)'''

def userHelp(error=''):
    from cheutils.usage import Usage
    u = Usage(help=sigpager_help, rcsid=sigpager_cset)
    u.printHelp(err=error)


def run():
    sigdir = signaturedir
    tail = suffix
    defsig = sigsep = inp = ''

    try:

        opts, args = getopt.getopt(sys.argv[1:], 'd:fhs:t:')
        for o, a in opts:
            if o == '-d':
                sigdir = a
            if o == '-f':
                sigsep = '-- \n'
            if o == '-h':
                userHelp()
            if o == '-s':
                defsig = a
            if o == '-t':
                tail = a
        if args == ['-']:
            inp = sys.stdin.read()
        else:
            targets = args

        s = Signature(sig=defsig, sdir=sigdir, sep=sigsep, tail=tail,
                inp=inp, targets=targets)
        s.underSign()

    except (getopt.GetoptError, SignatureError), e:
        userHelp(e)

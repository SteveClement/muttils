'''viewhtml - unpack html message and display with browser
'''

# $Id$

import email, email.errors, email.iterators, email.utils
import os.path, re, shutil, sys, tempfile, chardet
from muttils import pybrowser, ui, util

try:
    import inotifyx
except ImportError:
    import time


class viewhtml(pybrowser.browser):
    def __init__(self, safe, keep, app, args):
        self.ui = ui.ui()
        self.ui.updateconfig()
        pybrowser.browser.__init__(self, parentui=self.ui,
                                   app=app, evalurl=True)
        self.inp = args
        self.safe = safe or self.ui.configbool('html', 'safe')
        self.keep = keep
        if self.keep is None:
            self.keep = self.ui.configint('html', 'keep', 3)

    def cleanup(self, tmpdir):
        if self.keep:
            shutil.rmtree(tmpdir)

    def ivisit(self):
        try:
            fd = inotifyx.init()
            wd = inotifyx.add_watch(fd, self.items[0], inotifyx.IN_CLOSE)
            self.urlvisit()
            inotifyx.get_events(fd, self.keep)
            inotifyx.rm_watch(fd, wd)
            os.close(fd)
        except IOError:
            hint = ('consider increasing '
                    '/proc/sys/fs/inotify/max_user_watches')
            raise util.DeadMan('failed to enable inotify', hint=hint)

    def view(self):
        try:
            if self.inp:
                if len(self.inp) > 1:
                    raise util.DeadMan('only 1 argument allowed')
                fp = open(self.inp[0], 'rb', errors='replace')
            else:
                fp = sys.stdin
                try:
                    msg = email.message_from_file(fp)
                except UnicodeDecodeError:
                    print('This message has some strange unicode characters. Investigate manually.')
                    sys.exit(1)
            if self.inp:
                fp.close()
        except email.errors.MessageParseError as inst:
            raise util.DeadMan(inst)
        if not msg:
            raise util.DeadMan('input not a message')
        if not msg['message-id']:
            hint = ('make sure input is a raw message,'
                    ' in mutt: unset pipe_decode')
            raise util.DeadMan('no message-id found', hint=hint)
        htiter = email.iterators.typed_subpart_iterator(msg, subtype='html')
        try:
            html = next(htiter)
        except StopIteration:
            raise util.DeadMan('no html found')
        htmldir = tempfile.mkdtemp('', 'viewhtmlmsg.')
        try:
            htmlfile = os.path.join(htmldir, 'index.html')
            charsdet=chardet.detect(bytes(html.get_payload(decode=True)))
            if charsdet['confidence'] > 0.7:
                charset = chardet.detect(bytes(html.get_payload(decode=True)))['encoding']
            else:
                charset = html.get_param('charset')

            html = html.get_payload(decode=True).decode(charset)
            if charset:
                charsetmeta = '<meta charset="%s">' % charset
                if '<head>' in html:
                    html = html.replace('<head>', '<head>%s' % charsetmeta)
                else:
                    html = '<head>%s</head>%s' % (charsetmeta, html)
            fc = 0
            for part in msg.walk():
                fc += 1
                fn = (part.get_filename() or part.get_param('filename') or
                      part.get_param('name', 'prefix_%d' % fc))
                if part['content-id']:
                    # safe ascii filename: replace it with cid
                    fn = email.utils.unquote(part['content-id'])
                    html = html.replace('"cid:%s"' % fn, "%s" % fn)
                fpay = part.get_payload(decode=True)
                if fpay:
                    fp = open(os.path.join(htmldir, fn), 'wb')
                    fp.write(fpay)
                    fp.close()
            if self.safe:
                spat = r'(src|background)\s*=\s*["\']??https??://[^"\'>]*["\'>]'
                html = re.sub(spat, r'\1="#"', html)
            fp = open(htmlfile, 'wb')
            fp.write(bytes(html, charset))
            fp.close()
            self.items = [htmlfile]
            if self.keep:
                try:
                    self.ivisit()
                except NameError:
                    self.urlvisit()
                    time.sleep(self.keep)
            else:
                self.urlvisit()
        finally:
            self.cleanup(htmldir)

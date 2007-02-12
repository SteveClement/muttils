# $Id$

import iterm, kiosk, pybrowser, tpager, ui, urlcollector, util
from urlregex import mailcheck, ftpcheck
import os, readline

class UrlpagerError(Exception):
    '''Exception class for the urlpager module.'''

class Urlpager(urlcollector.urlcollector, tpager.tpager):

    options = {
            'proto': 'all',
            'files': None,
            'pat': None,
            'kiosk': '',
            'browse': False,
            'local': False,
            'mhiers': None,
            'mspool': True,
            'mask': None,
            'xb': False,
            'tb': False,
            'ftp': 'ftp',
            'getdir': '',
            }

    def __init__(self, parentui=None, opts={}):
        urlcollector.urlcollector.__init__(self)
        tpager.tpager.__init__(self, name='url')
        self.ui = parentui or ui.config()
        self.options.update(opts.items())
        for k in self.options.keys():
            setattr(self, k, self.options[k])

    def urlPager(self):
        if self.proto not in ('all', 'mid'):
            self.name = '%s %s' % (self.proto, self.name)
        elif self.proto == 'mid':
            self.name = 'message-id'
        self.name = 'unique %s' % self.name
        try:
            # as there is no ckey, interact() returns always 0
            self.interact()
        except tpager.TpagerError, inst:
            raise UrlpagerError(inst)

    def urlGo(self):
        url, cs, conny = self.items[0], [], True
        if (self.proto == 'mailto'
                or self.proto == 'all' and mailcheck(url)):
            try:
                self.ui.updateconfig()
                cs = [self.ui.configitem('messages', 'mailer')]
            except self.ui.ConfigError, inst:
                raise UrlpagerError(inst)
            conny = False
        elif self.getdir:
            cs = ['wget', '-P', self.getdir]
        elif self.proto == 'ftp' or ftpcheck(url):
            if not os.path.splitext(url)[1] and not url.endswith('/'):
                self.items = [url + '/']
            cs = [self.ftp]
        if not cs:
            try:
                b = pybrowser.browser(parentui=self.ui,
                        items=self.items, tb=self.tb, xb=self.xb)
                b.urlvisit()
            except pybrowser.BrowserError, e:
                raise UrlpagerError(e)
        else:
            cs += [url]
            if conny:
                util.goonline()
            if not os.isatty(0): # not connected to terminal
                tty = os.ctermid()
                cs += ['<', tty, '>', tty]
                os.system(' '.join(cs))
            else:
                os.execvp(cs[0], cs)

    def urlSearch(self):
        if self.proto != 'mid':
            try:
                self.ui.updateconfig()
                self.cpan = self.ui.configitem('can', 'cpan')
                self.ctan = self.ui.configitem('can', 'ctan')
            except self.ui.ConfigError, inst:
                raise UrlpagerError(inst)
        try:
            self.urlcollect()
        except urlcollector.UrlcollectorError, e:
            raise UrlpagerError(e)
        self.urlPager()
        if not self.items:
            return
        if self.proto != 'mid':
            try:
                if self.files:
                    readline.add_history(self.items[0])
                    url = raw_input('\n\npress <UP> or <C-P> to edit url, '
                            '<C-C> to cancel or <RET> to accept\n%s\n'
                            % self.items[0])
                else:
                    it = iterm.iterm()
                    it.terminit()
                    url = raw_input('\n\npress <RET> to accept or <C-C> to cancel, '
                            'or enter url manually\n%s\n' % self.items[0])
                    it.reinit()
                if url:
                    self.items = [url]
                self.urlGo()
            except KeyboardInterrupt:
                pass
        else:
            try:
                k = kiosk.kiosk(self.ui, items=self.items, opts=self.options)
                k.kioskstore()
            except kiosk.KioskError, inst:
                raise UrlpagerError(inst)

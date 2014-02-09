# -*- coding: utf-8 -*-
import os
import glob

import openerp.tests

fname, _ = os.path.splitext(__file__)

class TestUi(openerp.tests.HttpCase):
    def test(self):
        for i in glob.glob('%s*.js' % fname):
            self.phantomjs(i)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

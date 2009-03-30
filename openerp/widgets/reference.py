###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# The OpenERP web client is distributed under the "OpenERP Public License".
# It's based on Mozilla Public License Version (MPL) 1.1 with following 
# restrictions:
#
# -   All names, links and logos of Tiny, Open ERP and Axelor must be 
#     kept as in original distribution without any changes in all software 
#     screens, especially in start-up page and the software header, even if 
#     the application source code has been changed or updated or code has been 
#     added.
#
# -   All distributions of the software must keep source code with OEPL.
# 
# -   All integrations to any other software must keep source code with OEPL.
#
# If you need commercial licence to remove this kind of restriction please
# contact us.
#
# You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
#
###############################################################################

import turbogears as tg

from interface import TinyField
from form import Form
from listgrid import List

from openerp import rpc
from openerp import validators as tiny_validators

import many2one

class Reference(TinyField):

    template = "openerp.widgets.templates.reference"
    params = ['options','domain','context', "text", "relation"]

    options = []

    def __init__(self, attrs={}):
        super(Reference, self).__init__(attrs)
        self.options = attrs.get('selection', [])
        self.domain = []
        self.context = {}
        self.validator = tiny_validators.Reference()
        self.onchange = None # override onchange in js code

    def set_value(self, value):
        if value:
            self.relation, self.default = value.split(",")
            self.text = many2one.get_name(self.relation, self.default)
        else:
            self.relation = ''
            self.default = ''
            self.text = ''
            
# vim: ts=4 sts=4 sw=4 si et


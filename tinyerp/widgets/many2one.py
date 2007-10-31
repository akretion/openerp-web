###############################################################################
#
# Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################################################

import turbogears as tg

from tinyerp import rpc

from interface import TinyField
from form import Form
import validators as tiny_validators

def get_name(model, id):
    id = (id or False) and int(id)
    name = (id or str('')) and str(id)

    if model and id:
        proxy = rpc.RPCProxy(model)
        name = proxy.name_get([id], rpc.session.context.copy())
        name = name[0][1]

    return name

class M2O(TinyField):
    template = "tinyerp.widgets.templates.many2one"
    params=['relation', 'text', 'domain', 'context', 'link']

    domain = []
    context = {}
    link = 1

    def __init__(self, attrs={}):

        super(M2O, self).__init__(attrs)
        self.relation = attrs.get('relation', '')

        self.domain = attrs.get('domain', [])
        self.context = attrs.get('context', {})
        self.link = attrs.get('link')

        self.validator = tiny_validators.many2one()

    def set_value(self, value):
        if isinstance(value, tuple):
            value = value[0]

        self.default = value

    def update_params(self, d):
        super(M2O, self).update_params(d)
        d['text'] = get_name(self.relation, d['value'])

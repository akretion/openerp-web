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

"""
This module implementes search view for a tiny model. Currently it simply displays
list view of the given model.

@todo: implement read search window
"""
import cherrypy

from turbogears import expose
from turbogears import widgets
from turbogears import controllers

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from tinyerp import tools
from tinyerp import widgets_search as tws
from tinyerp.tinyres import TinyResource
from tinyerp.modules.utils import TinyDict

import form

def _search_string(name, type, value):
    if value:

        if type == 'many2many' or type == 'one2many' or type =='many2one' or type=='char':
            return name, 'ilike', value

        elif type== 'float' or type == 'integer' or type == 'datetime' or type=='date' or type=='time':
            if value[0] and value[1]:
                return [(name, '>=', value[0]), (name, '<=', value[1])]
            elif value[0]:
                return name, '>=', value[0]
            elif value[1]:
                return name, '<=', value[1]
            return None

        elif type=='boolean':
            return name, '=', int(value)

        elif  type=='selection':
            return name, '=', value

    return None

class Search(controllers.Controller, TinyResource):

    @expose(template="tinyerp.modules.gui.templates.search")
    def create(self, params, values={}):
        form = tws.search_view.ViewSearch(params, values=values, name="search_form", action='/search/ok')
        return dict(form=form)

    @expose()
    def ok(self, **kw):
        params, data = TinyDict.split(kw)

        ids = [int(id) for id in data.get('search_list', [])]

        if ids:
            if type(ids) == type([]):
                params.ids = [int(e) for e in ids]
            else:
                params.ids = [int(ids)]
            params.id = params.ids[0]

        return form.Form().create(params)

    @expose()
    def cancel(self, **kw):
        params, data = TinyDict.split(kw)
        return form.Form().create(params)

    @expose()
    def find(self, **kw):
        params, data = TinyDict.split(kw)

        fields_type = params.fields_type
        search_list = []

        if fields_type:
            for n, v in fields_type.items():
                t = _search_string(n, v, kw[n])
                if t:
                    if type(t) == type([]):
                        search_list += t
                    else:
                        search_list += [t]

        try:
            l = int(data.get('limit', '80'))
            o = int(data.get('offset', '0'))
        except:
            l = 80
            o = 0

        proxy = rpc.RPCProxy(params.model)
        params.found_ids = proxy.search(search_list, o, l)

        return self.create(params, data)

    @expose('json')
    def get_string(self, model, id):
        proxy = rpc.RPCProxy(model)
        name = proxy.name_get([id], {})
        return dict(name=name[0][1])


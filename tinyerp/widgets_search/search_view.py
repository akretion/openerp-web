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
import cherrypy

from tinyerp import rpc
from tinyerp.modules.utils import TinyDict


import tinyerp.widgets as tw
from tinyerp.widgets.interface import TinyCompoundWidget

import search

class ViewSearch(TinyCompoundWidget):

    template = "tinyerp.widgets_search.templates.search"

    member_widgets = ['form_view', 'list_view']

    def __init__(self, params, values={}, **kw):
        super(ViewSearch, self).__init__(params)

        self.model         = params.model
        self.state         = params.state or None
        self.id            = params.id or False
        self.ids           = params.ids
        self.found_ids     = params.found_ids or []
        self.view_ids      = params.view_ids or []
        self.view_mode     = params.view_mode or ['form', 'tree']
        self.view_mode2    = params.view_mode2 or ['tree', 'form']

        self.view_type     = self.view_mode[0]
        self.domain        = params.domain or []
        self.context       = params.context or {}

        proxy = rpc.RPCProxy(self.model)

        ctx = rpc.session.context.copy()
        view_form = proxy.fields_view_get({}, 'form', ctx)
        view_tree = proxy.fields_view_get({}, 'tree', ctx)

        self.form_view = search.Form(name=kw['name'], action=kw['action'], params=params, values=values)
        self.list_view = tw.list.List('search_list', model=self.model, ids=self.found_ids, view=view_tree, domain=self.domain, context=self.context, selectable=True, multiselect=not params.m2o and True)

        self.string = self.form_view.string


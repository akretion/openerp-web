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


import xml.dom.minidom
from elementtree import ElementTree as ET

import turbogears as tg
import cherrypy

from tinyerp import tools
from tinyerp import rpc

from interface import TinyCompoundWidget

import form
import list

class Screen(TinyCompoundWidget):
    template = """
    <span>
        <input type="hidden" name="${name}_terp_model" value="${model}"/>
        <input type="hidden" name="${name}_terp_state" value="${state}"/>
        <input type="hidden" name="${name}_terp_id" value="${str(id)}"/>
        <input type="hidden" name="${name}_terp_ids" value="${str(ids)}"/>
        <input type="hidden" name="${name}_terp_view_ids" value="${str(view_ids)}"/>
        <input type="hidden" name="${name}_terp_view_mode" value="${str(view_mode)}"/>
        <input type="hidden" name="${name}_terp_view_mode2" value="${str(view_mode2)}"/>
        <input type="hidden" name="${name}_terp_domain" value="${str(domain)}"/>
        <input type="hidden" name="${name}_terp_context" value="${str(context)}"/>

        ${widget.display(value_for(widget), **params_for(widget))}
    </span>
    """

    params = ['model', 'state', 'id', 'ids', 'view_ids', 'view_mode', 'view_mode2', 'domain', 'context']

    member_widgets = ['widget']
    widget = None

    def __init__(self, terp=None, prefix='', views_preloaded={}, selectable=False, editable=False):

        super(Screen, self).__init__(dict(prefix=prefix))

        # get terp dictionary
        terp = terp or cherrypy.request.terp

        self.model         = terp.model
        self.state         = terp.state or None
        self.id            = terp.id or None
        self.ids           = terp.ids
        self.view_ids      = terp.view_ids or []
        self.view_mode     = terp.view_mode or ['form', 'tree']
        self.view_mode2    = terp.view_mode2 or ['tree', 'form']

        self.view_type     = self.view_mode[0]
        self.domain        = terp.domain or []
        self.context       = terp.context or {}

        self.prefix             = prefix
        self.views_preloaded    = views_preloaded
        self.selectable         = selectable
        self.editable           = editable

        # Use False as view_id if switching the vuew
        if self.view_mode[0] != self.view_mode2[0]:
            self.view_ids = [False] + self.view_ids
        else:
            if False in self.view_ids: self.view_ids.remove(False)

        view_id = (self.view_ids or False) and self.view_ids[0]
        view_type = self.view_mode[0]

        if view_type in self.views_preloaded:
            view = self.views_preloaded[view_type]
        else:
            proxy = rpc.RPCProxy(self.model)
            view = proxy.fields_view_get(view_id, view_type, self.context)

        if view_type == 'form':
            self.widget = form.Form(prefix=prefix, model=self.model, view=view, ids=(self.id or []) and [self.id], editable=editable, selectable=selectable)
        else:
            self.widget = list.List(model=self.model, view=view, ids=self.ids, editable=editable, selectable=selectable)
            self.ids = self.widget.ids

        self.string = self.widget.string

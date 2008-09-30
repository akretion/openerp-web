###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
# Service Company
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################

import turbogears as tg
import cherrypy

from openerp import tools
from openerp import rpc
from openerp import cache

from interface import TinyCompoundWidget

import form
import graph
import listgrid

import tinycalendar

class Screen(TinyCompoundWidget):

    template = """
    <span xmlns:py="http://purl.org/kid/ns#" py:strip="">
        <input type="hidden" id="${name}_terp_model" name="${name}_terp_model" value="${model}"/>
        <input type="hidden" id="${name}_terp_state" name="${name}_terp_state" value="${state}"/>
        <input type="hidden" id="${name}_terp_id" name="${name}_terp_id" value="${str(id)}"/>
        <input type="hidden" id="${name}_terp_ids" name="${name}_terp_ids" value="${str(ids)}"/>
        <input type="hidden" id="${name}_terp_view_ids" name="${name}_terp_view_ids" value="${str(view_ids)}"/>
        <input type="hidden" id="${name}_terp_view_mode" name="${name}_terp_view_mode" value="${str(view_mode)}"/>
        <input type="hidden" id="${name}_terp_view_type" name="${name}_terp_view_type" value="${str(view_type)}"/>
        <input type="hidden" id="${name}_terp_view_id" name="${name}_terp_view_id" value="${str(view_id)}"/>
        <input type="hidden" id="${name}_terp_domain" name="${name}_terp_domain" value="${str(domain)}"/>
        <input type="hidden" id="${name}_terp_context" name="${name}_terp_context" value="${str(context)}"/>
        <input type="hidden" id="${name}_terp_editable" name="${name}_terp_editable" value="${editable}"/>

        <input type="hidden" id="${name}_terp_limit" name="${name}_terp_limit" value="${limit}"/>
        <input type="hidden" id="${name}_terp_offset" name="${name}_terp_offset" value="${offset}"/>
        <input type="hidden" id="${name}_terp_count" name="${name}_terp_count" value="${count}"/>

        <span py:if="widget" py:replace="widget.display(value_for(widget), **params_for(widget))"/>
    </span>
    """

    params = ['model', 'state', 'id', 'ids', 'view_id', 'view_ids', 'view_mode', 'view_type', 'domain', 'context', 'limit', 'offset', 'count']

    member_widgets = ['widget']
    widget = None

    def __init__(self, params=None, prefix='', name='', views_preloaded={}, hastoolbar=False, editable=False, readonly=False, selectable=0, nolinks=1):

        # get params dictionary
        params = params or cherrypy.request.terp_params
        prefix = prefix or (params.prefix or '')

        super(Screen, self).__init__(dict(prefix=prefix, name=name))

        self.model         = params.model
        self.state         = params.state or None
        self.id            = params.id or False
        self.ids           = params.ids
        self.view_ids      = params.view_ids or []
        self.view_mode     = params.view_mode or []
        self.view_type     = params.view_type
        self.view_id       = False
 
        while len(self.view_ids) < len(self.view_mode):
            self.view_ids += [False]

        if not self.view_type and params.view_mode:
            self.view_type = params.view_mode[0]
            
        if self.view_ids and self.view_type in self.view_mode:
            idx = self.view_mode.index(self.view_type)
            self.view_id = self.view_ids[idx]

        self.domain        = params.domain or []
        self.context       = params.context or {}
        self.nodefault     = params.nodefault or False

        self.offset        = params.offset
        self.limit         = params.limit
        self.count         = params.count       

        if (self.ids or self.id) and self.count == 0:
            self.count = rpc.RPCProxy(self.model).search_count(self.domain)

        self.prefix             = prefix
        self.views_preloaded    = views_preloaded or (params.views or {})

        self.hastoolbar         = hastoolbar
        self.toolbar            = None

        self.selectable         = selectable
        self.editable           = editable
        self.readonly           = readonly
        self.link               = nolinks

        # get calendar options
        self.kalendar           = params.kalendar

        if self.view_mode:
            self.add_view_id(self.view_id, self.view_type)

    def add_view_id(self, view_id, view_type):
        self.view_id = view_id

        self.view_id = view_id
        
        if view_type in self.views_preloaded:
            view = self.views_preloaded[view_type]
        else:
            ctx = rpc.session.context.copy()
            ctx.update(self.context)
            view = cache.fields_view_get(self.model, view_id, view_type, ctx, self.hastoolbar)

        self.add_view(view, view_type)

    def add_view(self, view, view_type='form'):

        self.view_id = view.get('view_id', self.view_id)

        if view_type == 'form':
            self.widget = form.Form(prefix=self.prefix,
                                    model=self.model,
                                    view=view,
                                    ids=(self.id or []) and [self.id],
                                    domain=self.domain,
                                    context=self.context,
                                    editable=self.editable,
                                    readonly=self.readonly,
                                    nodefault=self.nodefault, nolinks=self.link)
            
            if not self.ids:
                self.ids = (self.id or []) and [self.id]

        elif view_type == 'tree':
            self.widget = listgrid.List(self.name or '_terp_list',
                                        model=self.model,
                                        view=view,
                                        ids=self.ids,
                                        domain=self.domain,
                                        context=self.context,
                                        editable=self.editable,
                                        selectable=self.selectable,
                                        offset=self.offset, limit=self.limit, count=self.count, nolinks=self.link)

            self.ids = self.widget.ids
            self.count = self.widget.count

        elif view_type == 'graph':
            self.widget = graph.Graph(model=self.model, view_id=view.get('view_id', False), ids=self.ids, domain=self.domain, context=self.context)
            self.ids = self.widget.ids

        elif view_type == 'calendar':
            kmode = "week"
            if self.kalendar: kmode = self.kalendar.mode

            kwid = {"month": tinycalendar.MonthCalendar,
                    "week": tinycalendar.WeekCalendar,
                    "day": tinycalendar.DayCalendar,}

            self.widget = kwid[kmode](model=self.model, view=view, ids=self.ids, domain=self.domain, context=self.context, options=self.kalendar)

        self.string = (self.widget or '') and self.widget.string

        toolbar = {}
        for item, value in view.get('toolbar', {}).items():
            if value: toolbar[item] = value

        self.toolbar = toolbar or None
        self.hastoolbar = (toolbar or False) and True
        
# vim: ts=4 sts=4 sw=4 si et


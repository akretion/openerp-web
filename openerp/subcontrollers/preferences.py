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

import re
import time

from turbogears import expose
from turbogears import controllers
from turbogears import redirect

import cherrypy

from openerp import rpc
from openerp.tinyres import TinyResource
from openerp.utils import TinyDict

from openerp.widgets.screen import Screen

class Preferences(controllers.Controller, TinyResource):

    @expose(template="openerp.subcontrollers.templates.preferences")
    def create(self):
        proxy = rpc.RPCProxy('res.users')
        action_id = proxy.action_get({})
        
        action = rpc.RPCProxy('ir.actions.act_window').read([action_id], False, rpc.session.context)[0]

        view_ids=[]
        if action.get('views', []):
            view_ids=[x[0] for x in action['views']]
        elif action.get('view_id', False):
            view_ids=[action['view_id'][0]]
            
        params = TinyDict()
        params.id = rpc.session.uid
        params.ids = [params.id]
        params.model = 'res.users'
        params.view_type = 'form'
        params.view_mode = ['form']
        params.view_ids = view_ids

        screen = Screen(params, views_preloaded=action.get('views'), editable=True)
        screen.string = _('Preferences')
        
        return dict(screen=screen)

    @expose()
    def ok(self, **kw):
        params, data = TinyDict.split(kw)
        proxy = rpc.RPCProxy('res.users')
        proxy.write([rpc.session.uid], data)
        rpc.session.context_reload()
        raise redirect('/')
        
# vim: ts=4 sts=4 sw=4 si et


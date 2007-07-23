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

import os
import time

from turbogears import expose
from turbogears import controllers

import cherrypy

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from tinyerp.tinyres import TinyResource

from tinyerp.modules.utils import TinyDict
from tinyerp.modules.utils import TinyParent

import tinyerp.widgets as tw

class FieldPref(controllers.Controller, TinyResource):
    
    @expose(template="tinyerp.modules.gui.templates.fieldpref")
    def index(self, **kw): #_terp_model, _terp_field, _terp_deps
        params, data = TinyDict.split(kw)
        return dict(model=params.model, field=params.field, deps=params.deps, show_header_footer=False)
    
    @expose('json')
    def get(self, **kw):
        params, data = TinyDict.split(kw)
        
        field = params.field.split('/')
        
        prefix = '.'.join(field[:-1])
        field = field[-1]

        pctx = TinyParent(**kw)
        ctx = pctx[prefix] or pctx
       
        proxy = rpc.RPCProxy(params.model)
        res = proxy.fields_get(False, rpc.session.context)
        
        text = res[field].get('string')
        deps = []
        
        for name, attrs in res.items():
            if attrs.get('change_default', False):
                value = ctx.get(name)
                if value:
                    deps.append((name, name, value, value))
                
        return dict(text=text, deps=str(deps))
    
    @expose(template="tinyerp.modules.gui.templates.fieldpref")
    def save(self, **kw):
        params, data = TinyDict.split(kw)
        
        deps = False
        if params.deps:
            for n, v in params.deps.items():
                deps = "%s=%s" %(n,v)
                break

        model = params.model        
        field = params.field['name']        
        value = params.field['value']
        
        field = field.split('/')[-1]

        proxy = rpc.RPCProxy('ir.values')
        res = proxy.set('default', deps, field, [(model,False)], value, True, False, False, params.you or False, True)

        return dict(model=params.model, field=params.field, deps=params.deps2, should_close=True, show_header_footer=False)
    
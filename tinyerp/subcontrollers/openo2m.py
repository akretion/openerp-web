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

from turbogears import expose
from turbogears import widgets
from turbogears import validators
from turbogears import validate

import cherrypy

from tinyerp import rpc
from tinyerp import widgets as tw

from tinyerp.utils import TinyDict
from tinyerp.cache import cache

from form import Form

class OpenO2M(Form):
    
    path = '/openo2m'    # mapping from root
    
    def create_form(self, params, tg_errors=None):
             
        params.view_mode = ['form']
        params.view_type = 'form'
        
        form = super(OpenO2M, self).create_form(params, tg_errors=tg_errors)
        form.action = "/openo2m/save"

        form.hidden_fields = [widgets.HiddenField(name='_terp_parent_model', default=params.parent_model),
                              widgets.HiddenField(name='_terp_parent_id', default=params.parent_id),
                              widgets.HiddenField(name='_terp_o2m', default=params.o2m)]

        return form
    
    @expose(template="tinyerp.subcontrollers.templates.openo2m")
    def create(self, params, tg_errors=None):

        if tg_errors:
            form = cherrypy.request.terp_form
        else:
            form = self.create_form(params, tg_errors)        
        
        return dict(form=form, params=params, show_header_footer=False)
    
    def get_form(self):
        params, data = TinyDict.split(cherrypy.request.params)

        # bypass validations, if saving from button in non-editable view
        if params.button and not params.editable and params.id:
            return None

        cherrypy.request.terp_validators = {}

        params.nodefault = True

        form = self.create_form(params)
        cherrypy.request.terp_form = form

        vals = cherrypy.request.terp_validators
        schema = validators.Schema(**vals)

        form.validator = schema

        return form
    
    @expose()
    @validate(form=get_form)
    def save(self, terp_save_only=False, tg_errors=None, **kw):
        params, data = TinyDict.split(kw)        

        if tg_errors:
            return self.create(params, tg_errors=tg_errors)
       
        proxy = rpc.RPCProxy(params.parent_model)
        
        id = params.id or 0      
        data = {params.o2m : [(id and 1, id, data)]}

        id = proxy.write([params.parent_id], data, rpc.session.context)
        
        params.load_counter = 1
        if params.id:
            params.load_counter = 2
            
        return self.create(params)
    
    @expose()    
    def edit(self, **kw):
        params, data = TinyDict.split(kw)
        return self.create(params)
    
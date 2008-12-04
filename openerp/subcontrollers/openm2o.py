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

from turbogears import expose
from turbogears import widgets
from turbogears import validators
from turbogears import validate

import cherrypy

from openerp import rpc
from openerp import cache
from openerp import widgets as tw

from openerp.utils import TinyDict

from form import Form
from form import get_validation_schema

class OpenM2O(Form):
    
    path = '/openm2o'    # mapping from root
    
    @expose(template="openerp.subcontrollers.templates.openm2o")
    def create(self, params, tg_errors=None):
        
        params.editable = params.get('_terp_editable', True)
        form = self.create_form(params, tg_errors)
        
        form.hidden_fields = [widgets.HiddenField(name='_terp_m2o', default=params.m2o)]

        return dict(form=form, params=params, show_header_footer=False)
    
    @expose()
    @validate(form=get_validation_schema)
    def save(self, terp_save_only=False, tg_errors=None, **kw):
        params, data = TinyDict.split(kw)
        
        # remember the current notebook tab
        cherrypy.session['remember_notebook'] = True

        if tg_errors:
            return self.create(params, tg_errors=tg_errors)

        # bypass save, for button action in non-editable view
        if not (params.button and not params.editable and params.id):

            proxy = rpc.RPCProxy(params.model)

            if not params.id:
                id = proxy.create(data, params.context)
                params.ids = (params.ids or []) + [int(id)]
                params.id = int(id)
                params.count += 1
            else:
                id = proxy.write([params.id], data, params.context)

        button = (params.button or False) and True

        # perform button action
        if params.button:
            res = self.button_action(params)
            if res:
                return res

        current = params.chain_get(params.source or '')
        if current:
            current.id = None
            if not params.id:
                params.id = int(id)
        elif not button:
            params.editable = False

        if not current and not button:
            params.load_counter = 2
            
        return self.create(params)
    
    @expose()    
    def edit(self, **kw):
        params, data = TinyDict.split(kw)
        
        if not params.model:
            params.update(kw)
            
        params.view_mode = ['form', 'tree']
        params.view_type = 'form'
        
        params.editable = params.get('_terp_editable', True)
        
        return self.create(params)

# vim: ts=4 sts=4 sw=4 si et


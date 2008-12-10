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

"""
This module implementes search view for a tiny model. Currently it simply displays
list view of the given model.
"""
import cherrypy

from turbogears import expose
from turbogears import widgets
from turbogears import redirect
from turbogears import controllers
from turbogears import validators
from turbogears import validate

from openerp import rpc
from openerp import tools
from openerp import common

from openerp import widgets as tw
from openerp import widgets_search as tws

from openerp.tinyres import TinyResource

from openerp.utils import TinyDict
from openerp.utils import TinyForm

from form import Form

class Search(Form):

    @expose(template="openerp.subcontrollers.templates.search")
    def create(self, params, tg_errors=None):

        params.view_mode = ['tree', 'form']
        params.view_type = 'tree'

        params.offset = params.offset or 0
        params.limit = params.limit or 20
        params.count = params.count or 0

        params.editable = 0

        form = self.create_form(params, tg_errors)

        # don't show links in list view, except the do_select link
        form.screen.widget.show_links = 0

        return dict(form=form, params=params, show_header_footer=False)

    @expose()
    def new(self, model, source=None, kind=0, text=None, domain=[], context={}):
        """Create new search view...

        @param model: the model
        @param source: the source, in case of m2m, m2o search
        @param kind: 0=normal, 1=m2o, 2=m2m
        @param text: do `name_search` if text is provided
        @param domain: the domain
        @param context: the context
        """

        params = TinyDict()

        params.model = model
        params.domain = domain
        params.context = context

        params.source = source
        params.selectable = kind

        ctx = rpc.session.context.copy()
        ctx.update(params.context or {})
        params.ids = []
        proxy = rpc.RPCProxy(model)
        ids = proxy.name_search(text or '', params.domain or [], 'ilike', ctx)
        if ids:
            params.ids = [id[0] for id in ids]
            params.count = len(ids)

        return self.create(params)

    @expose('json')
    def eval_domain_and_context(self, **kw):
        params, data = TinyDict.split(kw)
        
        domain = params.domain
        context = params.context
        parent_context = params.parent_context or {}
        
        parent_context.update(rpc.session.context.copy())

        ctx = TinyForm(**kw).to_python()
        pctx = ctx

        prefix = params.prefix
        if prefix:
            ctx = ctx.chain_get(prefix)

        if prefix and '/' in prefix:
            prefix = prefix.rsplit('/', 1)[0]
            pctx = pctx.chain_get(prefix)

        ctx['parent'] = pctx
        ctx['context'] = parent_context

        if isinstance(domain, basestring):
            domain = eval(domain, ctx)  
        
        if isinstance(context, basestring):
            if not context.startswith('{'):
                context = "dict(%s)"%context
                ctx['dict'] = dict # required
            
            ctx['active_id'] = params.parent_id or False
            context = eval(context, ctx)

#           Fixed many2one pop up in listgrid when value is None.
            for key, val in context.items():
                if val==None:
                    context[key] = False

        return dict(domain=ustr(domain), context=ustr(context))

    @expose('json')
    def ok(self, **kw):
        params, data = TinyDict.split(kw)

        ids = [int(id) for id in data.get('search_list', [])]
        return dict(ids=ids)

    @expose('json')
    def get_name(self, model, id):
        name = tw.many2one.get_name(model, id)
        if not name:
            name=''
        return dict(name=name)

    @expose('json')
    def get_matched(self, model, text, **kw):
        params, data = TinyDict.split(kw)

        domain = params.domain or []
        context = params.context or {}
        
        ctx = rpc.session.context.copy()
        ctx.update(context)

        proxy = rpc.RPCProxy(model)
        values = proxy.name_search(text, domain, 'ilike', ctx)
        
        return dict(values=values)

    @expose()
    def get_m2m(self, model, ids, list_id):
        if not ids:
            ids='[]'
        ids = eval(ids)

        if not isinstance(ids, (list, tuple)): ids = [ids]

        m2m = tw.many2many.M2M(dict(relation=model, value=ids, name=list_id))
        return m2m.screen.render()
    
# vim: ts=4 sts=4 sw=4 si et


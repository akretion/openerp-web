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

from openerp.tools import expose
from openerp.tools import redirect

from openerp import rpc
from openerp import tools
from openerp import common

from openerp import widgets as tw
from openerp import widgets_search as tws

from openerp.controllers.base import SecuredController
from openerp.controllers import actions

from openerp.utils import TinyDict
from openerp.utils import TinyForm
from openerp.utils import TinyFormError

from form import Form

class Search(Form):

    path = '/search'    # mapping from root

    @expose(template="templates/search.mako")
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

        return dict(form=form, params=params)

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

        domain = kw.get('_terp_domain', [])
        context = kw.get('_terp_context', {})
        
        parent_context = params.parent_context or {}
        parent_context.update(rpc.session.context.copy())
        
        try:
            ctx = TinyForm(**kw).to_python()
            pctx = ctx
        except TinyFormError, e:
            return dict(error_field=e.field, error=ustr(e))
        except Exception, e:
            return dict(error=ustr(e))

        prefix = params.prefix
        if prefix:
            ctx = ctx.chain_get(prefix)

        if prefix and '/' in prefix:
            prefix = prefix.rsplit('/', 1)[0]
            pctx = pctx.chain_get(prefix)

        ctx['parent'] = pctx
        ctx['context'] = parent_context
        ctx['active_id'] = params.active_id or False
        ctx['active_ids'] = params.active_ids or []
        
        if params.active_id and not params.active_ids:
            ctx['active_ids'] = [params.active_id]
        
        if isinstance(domain, basestring):
            domain = tools.expr_eval(domain, ctx)
            
        if domain and len(domain) >= 2 and domain[-2] in ['&', '|']: # For custom domain ('AND', OR') from search view.
            dom1 = domain[-1:]
            dom2 = domain[:-2]
            domain = dom2 + dom1
        
        if isinstance(context, basestring):
            if not context.startswith('{'):
                context = "dict(%s)"%context
                ctx['dict'] = dict # required

            context = tools.expr_eval(context, ctx)

#           Fixed many2one pop up in listgrid when value is None.
            for key, val in context.items():
                if val==None:
                    context[key] = False
                    
        ctx2 = parent_context
        context.update(ctx2)
        
        return dict(domain=ustr(domain), context=ustr(context))

    @expose('json')
    def get(self, **kw):
        
        params, data = TinyDict.split(kw)
        
        model = params.model
        context = rpc.session.context
        
        record = kw.get('record')
        record = eval(record)
        
        proxy = rpc.RPCProxy(model)
        data = {}
        
        frm = {}
        error = ''
        values = {}
        
        for key, val in record.items():
            id = key
            for field in val:            
                fld = {}
                datas = {}
                res = proxy.fields_get(field)
            
                fld['value'] = val[field]
                fld['type'] = res[field].get('type')
       
                data[field] = fld
                try:
                    frm = TinyForm(**data).to_python()
                except Exception, e:
                    error = ustr(e)
                    error_field = ustr(e.field)
                    return dict(error=error, error_field=error_field)
                
                datas['rec'] = field
                
                if isinstance(frm[field], bool):
                    if frm[field]:
                        datas['rec_val'] = 1
                    else:
                        datas['rec_val'] = 0
                else:
                    datas['rec_val'] = frm[field]
                
            values[key] = datas
            
        return dict(frm=values, error=error)


    @expose('json')
    def eval_domain_filter(self, **kw):
        
        all_domains = kw.get('all_domains')
        custom_domains = kw.get('custom_domain')
        model = kw.get('model')
        
        all_domains = eval(all_domains)
        
        domains = all_domains.get('domains')
        selection_domain = all_domains.get('selection_domain')
        
        if domains: 
            domains = eval(domains)
            
        context = rpc.session.context
        
        domain = []
        check_domain = []
        check_domain = all_domains.get('check_domain')
        
        if check_domain and isinstance(check_domain, basestring):
            domain = tools.expr_eval(check_domain, context)
        
        if domain == None:
            domain = []
        
        if domains:
            for key in domains:
                domain += [(key, '=', domains[key])]
        
        if custom_domains:
            inner_domain = []
            tmp_domain = ''
            
            custom_domains = eval(custom_domains)
            
            for inner in custom_domains:
                if len(inner) == 4:
                    if isinstance(inner[3], int):
                        tmp_domain += '[\'' + inner[0] + '\', (\'' + inner[1] + '\', \'' + inner[2] + '\', ' + ustr(inner[3]) + ')]'
                    else:
                        tmp_domain += '[\'' + inner[0] + '\', (\'' + inner[1] + '\', \'' + inner[2] + '\', \'' + inner[3] + '\')]'
                elif len(inner) == 3:
                    if isinstance(inner[2], int):
                        tmp_domain += '[(\'' + inner[0] + '\', \'' + inner[1] + '\', ' + ustr(inner[2]) + ')]'
                    else:
                        tmp_domain += '[(\'' + inner[0] + '\', \'' + inner[1] + '\', \'' + inner[2] + '\')]'
            
            if tmp_domain :
                cust_domain = tmp_domain.replace('][', ', ')
                domain += eval(cust_domain)
        
        if selection_domain:
            if selection_domain in ['blk', 'sh', 'sf', 'mf']:
                if selection_domain == 'blk':
                    selection_domain = []
                
                if selection_domain in ['sh', 'sf']:
                    return dict(flag=selection_domain, sf_dom=ustr(domain))
                
                if selection_domain == 'mf':
                    act = {'name':'Manage Filters', 
                         'res_model':'ir.actions.act_window', 
                         'type':'ir.actions.act_window', 
                         'view_type':'form', 
                         'view_mode':'tree,form', 
                         'domain':'[(\'filter\',\'=\',True), (\'res_model\',\'=\',\'' + model + '\'), (\'default_user_ids\',\'in\', (\'' + str(rpc.session.uid) + '\',))]'}
                    return dict(action=act)
            else:
                selection_domain = eval(selection_domain)
                domain += selection_domain
        
        if not domain:
            domain = None
            
        return dict(domain=ustr(domain))

    @expose()
    def manage_filter(self, **kw):
        action = kw.get('action')
        action = eval(action)
        
        return actions.execute(action, context=rpc.session.context)

    @expose(template="templates/save_filter.mako")
    def save_filter(self, **kw):
        
        search_view_id = kw.get('search_view_id')
        model = kw.get('model')
        domain = kw.get('domain')
        flag = kw.get('flag')
        sc_id = kw.get('sc_id')
        
        return dict(search_view_id=search_view_id, model=model, domain=domain, flag=flag, sc_id=sc_id)
    
    @expose()
    def do_filter_sc(self, **kw):
        
        name = kw.get('sc_name')
        model = kw.get('model')
        domain = kw.get('domain')
        flag = kw.get('flag')
        id = kw.get('sc_id')
        
        datas = {'name': name, 
               'res_model': model, 
               'domain': domain, 
               'context': str({}), 
               'search_view_id': kw.get('search_view_id'), 
               'filter': True, 
               'default_user_ids': [[6, 0, [rpc.session.uid]]], 
               }
        action_id = rpc.session.execute('object', 'execute', 'ir.actions.act_window', 'create', datas)

        if flag == 'sh':
            parent_menu_id = rpc.session.execute('object', 'execute', 'ir.ui.menu', 'search', [('name','=','Custom Shortcuts')])
            
            if parent_menu_id:
                menu_data = {'name': name,
                           'sequence': 20,
                           'action': 'ir.actions.act_window,' + str(action_id),
                           'parent_id': parent_menu_id[0],
                           }
                
                menu_id = rpc.session.execute('object', 'execute', 'ir.ui.menu', 'create', menu_data)
                sc_data = {'name': name,
                         'sequence': 1,
                         'res_id': menu_id,
                         }
                shortcut_id = rpc.session.execute('object', 'execute', 'ir.ui.view_sc', 'create', sc_data)
        
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


# vim: ts=4 sts=4 sw=4 si et


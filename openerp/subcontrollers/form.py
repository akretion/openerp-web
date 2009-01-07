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

import re
import base64

from turbogears import expose
from turbogears import widgets
from turbogears import controllers
from turbogears import validators
from turbogears import validate
from turbogears import redirect
from turbogears import error_handler
from turbogears import exception_handler

import cherrypy

from openerp import rpc
from openerp import tools
from openerp import common

from openerp import widgets as tw
from openerp.tinyres import TinyResource

from openerp.utils import TinyDict
from openerp.utils import TinyForm

def make_domain(name, value):
    """A helper function to generate domain for the given name, value pair.
    Will be used for search window...
    """

    if isinstance(value, int) and not isinstance(value, bool):
        return [(name, '=', value)]

    if isinstance(value, dict):

        start = value.get('from')
        end = value.get('to')

        if start and end:
            return [(name, '>=', start), (name, '<=', end)]

        elif start:
            return [(name, '>=', start)]

        elif end:
            return [(name, '<=', end)]

        return None

    if isinstance(value, basestring) and value:
        return [(name, 'ilike', value)]

    if isinstance(value, bool) and value:
        return [(name, '=', 1)]

    return []

def search(model, offset=0, limit=20, domain=[], context={}, data={}):
    """A helper function to search for data by given criteria.

    @param model: the resource on which to make search
    @param offset: offset from when to start search
    @param limit: limit of the search result
    @param domain: the domain (search criteria)
    @param context: the context
    @param data: the form data

    @returns dict with list of ids count of records etc.
    """

    domain = domain or []
    context = context or {}
    data = data or {}

    search_domain = domain[:]
    search_data = {}

    for k, v in data.items():
        t = make_domain(k, v)

        if t:
            search_domain += t
            search_data[k] = v

    l = limit
    o = offset

    if l < 1: l = 20
    if o < 0: o = 0

    proxy = rpc.RPCProxy(model)
    ctx = rpc.session.context.copy()
    ctx.update(context)

    ids = proxy.search(search_domain, o, l, 0, ctx)
    count = proxy.search_count(search_domain, ctx)

    return dict(model=model, ids=ids, count=count, offset=o, limit=l,
                search_domain=search_domain, search_data=search_data)

def get_validation_schema(self):
    """Generate validation schema for the given Form instance. Should be used 
    to validate form inputs with @validate decorator.

    @param self: and instance of Form

    @returns a new instance of Form with validation schema
    """

    kw = cherrypy.request.params
    params, data = TinyDict.split(kw)

    # bypass validations, if saving from button in non-editable view
    if params.button and not params.editable and params.id:
        return None

    cherrypy.request.terp_validators = {}
    params.nodefault = True
        
    form = self.create_form(params)
    cherrypy.request.terp_form = form

    vals = cherrypy.request.terp_validators
    keys = vals.keys()
    for k in keys:
        if k not in kw:
            vals.pop(k)

    form.validator = validators.Schema(**vals)
    return form

def default_error_handler(self, tg_errors=None, **kw):
    """ Error handler for the given Form instance.

    @param self: an instance for Form
    @param tg_errors: errors
    """
    params, data = TinyDict.split(kw)
    return self.create(params, tg_errors=tg_errors)

def default_exception_handler(self, tg_exceptions=None, **kw):
    """ Exception handler for the given Form instance.

    @param self: an instance for Form
    @param tg_exceptions: exception
    """
    # let _cp_on_error handle the exception
    raise tg_exceptions

class Form(controllers.Controller, TinyResource):

    path = '/form'    # mapping from root

    def create_form(self, params, tg_errors=None):
        if tg_errors:
            return cherrypy.request.terp_form

        params.offset = params.offset or 0
        params.limit = params.limit or 20
        params.count = params.count or 0
        params.view_type = params.view_type or params.view_mode[0]

        form = tw.form_view.ViewForm(params, name="view_form", action="/form/save")

        if 'remember_notebook' in cherrypy.session:
            cherrypy.session.pop('remember_notebook')
        else:
            self.del_notebook_cookies()

        return form

    @expose(template="openerp.subcontrollers.templates.form")
    def create(self, params, tg_errors=None):

        params.view_type = params.view_type or params.view_mode[0]

        if params.view_type == 'tree':
            params.editable = True

        form = self.create_form(params, tg_errors)

        editable = form.screen.editable
        mode = form.screen.view_type
        id = form.screen.id
        ids = form.screen.ids

        buttons = TinyDict()    # toolbar
        links = TinyDict()      # bottom links (customise view, ...)
        
        buttons.new = not editable or mode == 'tree'
        buttons.edit = not editable and mode == 'form'
        buttons.save = editable and mode == 'form'
        buttons.cancel = editable and mode == 'form'
        buttons.delete = not editable and mode == 'form'
        buttons.pager =  mode == 'form' # Pager will visible in edit and non-edit mode in form view.

        buttons.search = 'tree' in params.view_mode and mode != 'tree'
        buttons.graph = 'graph' in params.view_mode and mode != 'graph'
        buttons.form = 'form' in params.view_mode and mode != 'form'
        buttons.calendar = 'calendar' in params.view_mode and mode != 'calendar'
        buttons.gantt = 'gantt' in params.view_mode and mode != 'gantt'
        buttons.can_attach = id and mode == 'form'
        buttons.has_attach = buttons.can_attach and self._has_attachments(params.model, id, mode)
        buttons.i18n = not editable and mode == 'form'

        target = params.context.get('_terp_target')
        buttons.toolbar = target != 'new' and not form.is_dashboard

        links.view_manager = True
        links.workflow_manager = False
        
        proxy = rpc.RPCProxy('workflow')
        wkf_ids = proxy.search([('osv', '=', params.model)], 0, 0, 0, rpc.session.context)
        links.workflow_manager = (wkf_ids or False) and wkf_ids[0]
        
        pager = None
        if buttons.pager:
            pager = tw.pager.Pager(id=form.screen.id, ids=form.screen.ids, offset=form.screen.offset, 
                                   limit=form.screen.limit, count=form.screen.count, view_type=params.view_type)

        return dict(form=form, pager=pager, buttons=buttons, links=links, path=self.path, show_header_footer=target!='new')

    def _has_attachments(self, model, id, mode):
        if mode <> 'form':
            return False
        proxy = rpc.RPCProxy('ir.attachment')
        cpt = proxy.search_count([('res_model', '=', model), ('res_id', '=', id)])
        return cpt > 0

    @expose()
    def edit(self, model, id=False, ids=None, view_ids=None, view_mode=['form', 'tree'], 
             source=None, domain=[], context={}, offset=0, limit=20, count=0, search_domain=None):

        params, data = TinyDict.split({'_terp_model': model,
                                       '_terp_id' : id,
                                       '_terp_ids' : ids,
                                       '_terp_view_ids' : view_ids,
                                       '_terp_view_mode' : view_mode,
                                       '_terp_source' : source,
                                       '_terp_domain' : domain,
                                       '_terp_context' : context,
                                       '_terp_offset': offset,
                                       '_terp_limit': limit,
                                       '_terp_count': count,
                                       '_terp_search_domain': search_domain})

        params.editable = True
        params.view_type = 'form'

        if params.view_mode and 'form' not in params.view_mode:
            params.view_type = params.view_mode[-1]
            
        if params.view_type == 'tree':
            params.view_type = 'form'
            
        if not params.ids:
            params.count = 1
            params.offset = 0

        # On New O2M
        if params.source:
            current = TinyDict()
            current.id = False
            current.view_type = 'form'
            params[params.source] = current

        return self.create(params)

    @expose()
    def view(self, model, id, ids=None, view_ids=None, view_mode=['form', 'tree'], 
            domain=[], context={}, offset=0, limit=20, count=0, search_domain=None):
        params, data = TinyDict.split({'_terp_model': model,
                                       '_terp_id' : id,
                                       '_terp_ids' : ids,
                                       '_terp_view_ids' : view_ids,
                                       '_terp_view_mode' : view_mode,
                                       '_terp_domain' : domain,
                                       '_terp_context' : context,
                                       '_terp_offset': offset,
                                       '_terp_limit': limit,
                                       '_terp_count': count,
                                       '_terp_search_domain': search_domain})

        params.editable = False
        params.view_type = 'form'

        if params.view_mode and 'form' not in params.view_mode:
            params.view_type = params.view_mode[-1]
            
        if params.view_type == 'tree':
            params.view_type = 'form'
            
        if not params.ids:
            params.count = 1
            params.offset = 0

        return self.create(params)

    @expose()
    def cancel(self, **kw):
        params, data = TinyDict.split(kw)

        if params.button:
            res = self.button_action(params)
            if res:
                return res
            raise redirect('/')

        if not params.id and params.ids:
            params.id = params.ids[0]

        if params.id and params.editable:
            raise redirect(self.path + "/view", model=params.model,
                                               id=params.id,
                                               ids=ustr(params.ids),
                                               view_ids=ustr(params.view_ids),
                                               view_mode=ustr(params.view_mode),
                                               domain=ustr(params.domain),
                                               context=ustr(params.context),
                                               offset=params.offset,
                                               limit=params.limit,
                                               count=params.count,
                                               search_domain=ustr(params.search_domain))

        params.view_type = 'tree'
        return self.create(params)

    @expose()
    @validate(form=get_validation_schema)
    @error_handler(default_error_handler)
    @exception_handler(default_exception_handler)
    def save(self, terp_save_only=False, **kw):
        """Controller method to save/button actions...

        @param tg_errors: TG special arg, used durring validation
        @param kw: keyword arguments

        @return: form view
        """
        params, data = TinyDict.split(kw)

        # remember the current notebook tab
        cherrypy.session['remember_notebook'] = True

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

        button = params.button

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

        if terp_save_only:
            return dict(params=params, data=data)

        args = {'model': params.model,
                'id': params.id,
                'ids': ustr(params.ids),
                'view_ids': ustr(params.view_ids),
                'view_mode': ustr(params.view_mode),
                'domain': ustr(params.domain),
                'context': ustr(params.context),
                'offset': params.offset,
                'limit': params.limit,
                'count': params.count,
                'search_domain': ustr(params.search_domain)}

        if params.editable or params.source or params.return_edit:
            raise redirect(self.path + '/edit', source=params.source, **args)

        raise redirect(self.path + '/view', **args)

    def button_action(self, params):

        button = params.button

        name = ustr(button.name)
        name = name.rsplit('/', 1)[-1]

        btype = button.btype
        model = button.model
        id = button.id or params.id

        id = (id or False) and int(id)
        ids = (id or []) and [id]
        
        if btype == 'cancel':
            if name:
                button.btype = "object"
                params.id = False
                res = self.button_action(params)
                if res:
                    return res

            return """<html>
        <head>
            <script type="text/javascript">
                window.onload = function(evt){
                    if (window.opener) {
                        window.opener.setTimeout("window.location.reload()", 0);
                        window.close();
                    } else {
                        window.location.href = '/';
                    }
                }
            </script>
        </head>
        <body></body>
        </html>"""
        
        elif btype == 'save':
            params.id = False

        elif btype == 'workflow':
            res = rpc.session.execute('object', 'exec_workflow', model, name, id)
            if isinstance(res, dict):
                from openerp.subcontrollers import actions
                return actions.execute(res, ids=[id])

        elif btype == 'object':
            ctx = params.context or {}
            ctx.update(rpc.session.context.copy())
            res = rpc.session.execute('object', 'execute', model, name, ids, ctx)

            if isinstance(res, dict):
                from openerp.subcontrollers import actions
                return actions.execute(res, ids=[id])

        elif btype == 'action':
            from openerp.subcontrollers import actions

            action_id = int(name)
            action_type = actions.get_action_type(action_id)

            if action_type == 'ir.actions.wizard':
                cherrypy.session['wizard_parent_form'] = self.path
                cherrypy.session['wizard_parent_params'] = params

            res = actions.execute_by_id(action_id, type=action_type, 
                                        model=model, id=id, ids=ids, 
                                        context=params.context or {})
            if res:
                return res

        else:
            raise common.warning(_('Invalid button type'))

        params.button = None

    @expose()
    def duplicate(self, **kw):
        params, data = TinyDict.split(kw)
        
        id = params.id
        ctx = params.context
        model = params.model
        
        proxy = rpc.RPCProxy(model)
        new_id = False
        try:
            new_id = proxy.copy(id, {}, ctx)
        except Exception, e:
            pass

        if new_id:
            params.id = new_id
            params.ids += [int(new_id)]
            params.count += 1

        args = {'model': params.model,
                'id': params.id,
                'ids': ustr(params.ids),
                'view_ids': ustr(params.view_ids),
                'view_mode': ustr(params.view_mode),
                'domain': ustr(params.domain),
                'context': ustr(params.context),
                'offset': params.offset,
                'limit': params.limit,
                'count': params.count,
                'search_domain': ustr(params.search_domain)}

        if new_id:
            raise redirect(self.path + '/edit', **args)

        raise redirect(self.path + '/view', **args)

    @expose()
    def delete(self, **kw):
        params, data = TinyDict.split(kw)

        current = params.chain_get(params.source or '') or params

        proxy = rpc.RPCProxy(current.model)

        idx = -1
        if current.id:
            res = proxy.unlink([current.id])
            idx = current.ids.index(current.id)
            current.ids.remove(current.id)
            params.count = 0 # invalidate count

            if idx == len(current.ids):
                idx = -1

        current.id = (current.ids or None) and current.ids[idx]

        self.del_notebook_cookies()

        args = {'model': params.model,
                'id': params.id,
                'ids': ustr(params.ids),
                'view_ids': ustr(params.view_ids),
                'view_mode': ustr(params.view_mode),
                'domain': ustr(params.domain),
                'context': ustr(params.context),
                'offset': params.offset,
                'limit': params.limit,
                'count': params.count,
                'search_domain': ustr(params.search_domain)}

        if not params.id:
            raise redirect(self.path + '/edit', **args)

        raise redirect(self.path + '/view', **args)

    @expose(content_type='application/octet-stream')
    def save_binary_data(self, _fname='file.dat', **kw):
        params, data = TinyDict.split(kw)
        
        cherrypy.response.headers['Content-Disposition'] = 'filename="%s"' % _fname;

        if params.datas:
            form = params.datas['form']
            res = form.get(params.field)
            return base64.decodestring(res)

        proxy = rpc.RPCProxy(params.model)
        res = proxy.read([params.id],[params.field], rpc.session.context)

        return base64.decodestring(res[0][params.field])

    @expose()
    def clear_binary_data(self, **kw):
        params, data = TinyDict.split(kw)

        proxy = rpc.RPCProxy(params.model)
        if params.fname:
            proxy.write([params.id], {params.field: False, params.fname: False})
        else:
            proxy.write([params.id], {params.field: False})

        return self.create(params)

    @expose()
    @validate(form=get_validation_schema)
    @error_handler(default_error_handler)
    @exception_handler(default_exception_handler)
    def filter(self, **kw):
        params, data = TinyDict.split(kw)

        l = params.limit or 20
        o = params.offset or 0
        c = params.count or 0
        
        id = params.id or False
        ids = params.ids or []
        
        filter_action = params.filter_action
        
        if ids and filter_action == 'FIRST':
            o = 0
            id = ids[0]
            
        if ids and filter_action == 'LAST':
            o = c - c % l
            id = ids[-1]

        if ids and filter_action == 'PREV':
            if id == ids[0]:
                o -= l
            elif id in ids:
                id = ids[ids.index(id)-1]

        if ids and filter_action == 'NEXT':
            if id == ids[-1]:
                o += l
            elif id in ids:
                id = ids[ids.index(id)+1]

        if filter_action:
            # remember the current notebook tab
            cherrypy.session['remember_notebook'] = True

        if params.offset != o:
    
            domain = params.domain    
            if params.search_domain is not None:
                domain = params.search_domain
                data = params.search_data
                
            res = search(params.model, o, l, domain=domain, data=data)
            
            o = res['offset']
            l = res['limit']
            c = res['count']
            
            params.search_domain = res['search_domain']
            params.search_data = res['search_data']
            
            ids = res['ids']
            id = False
            
            if ids and filter_action in ('FIRST', 'NEXT'):
                id = ids[0]
            
            if ids and filter_action in ('LAST', 'PREV'):
                id = ids[-1]

        params.id = id
        params.ids = ids
        params.offset = o
        params.limit = l
        params.count = c
        
        return self.create(params)
    
    @expose()
    def find(self, **kw):
        kw['_terp_offset'] = None
        kw['_terp_limit'] = None

        kw['_terp_search_domain'] = None
        kw['_terp_search_data'] = None

        return self.filter(**kw)

    @expose()
    def first(self, **kw):
        kw['_terp_filter_action'] = 'FIRST'
        return self.filter(**kw)

    @expose()
    def last(self, **kw):
        kw['_terp_filter_action'] = 'LAST'
        return self.filter(**kw)

    @expose()
    def previous(self, **kw):
        if '_terp_source' in kw:
            return self.previous_o2m(**kw)

        kw['_terp_filter_action'] = 'PREV'
        return self.filter(**kw)

    @expose()
    def next(self, **kw):
        if '_terp_source' in kw:
            return self.next_o2m(**kw)

        kw['_terp_filter_action'] = 'NEXT'
        return self.filter(**kw)

    @expose()
    def previous_o2m(self, **kw):
        params, data = TinyDict.split(kw)

        current = params.chain_get(params.source or '') or params

        idx = -1

        if current.id:

            # save current record
            if params.editable:
                self.save(terp_save_only=True, **kw)

            idx = current.ids.index(current.id)
            idx = idx-1

            if idx == len(current.ids):
                idx = len(current.ids) -1

        if current.ids:
            current.id = current.ids[idx]

        return self.create(params)

    @expose()
    def next_o2m(self, **kw):
        params, data = TinyDict.split(kw)
        c = params.count or 0

        current = params.chain_get(params.source or '') or params

        idx = 0

        if current.id:

            # save current record
            if params.editable:
                self.save(terp_save_only=True, **kw)

            idx = current.ids.index(current.id)
            idx = idx + 1

            if idx == len(current.ids):
                idx = 0

        if current.ids:
            current.id = current.ids[idx]

        return self.create(params)

    @expose()
    def switch(self, **kw):
        params, data = TinyDict.split(kw)  
        
        # switch the view
        params.view_type = params.source_view_type
        return self.create(params)

    @expose()
    def switch_o2m(self, **kw):
        
        params, data = TinyDict.split(kw)
        current = params.chain_get(params.source or '') or params

        current.view_type = params.source_view_type

        current.ids = current.ids or []
        if not current.id and current.ids:
            current.id = current.ids[0]
                   
        try:
            frm = self.create_form(params)
            wid = frm.screen.get_widgets_by_name(params.source)[0]
        except Exception, e:
            return 'ERROR: ' + str(e)
        
        return wid.render()
        
    def do_action(self, name, adds={}, datas={}):
        params, data = TinyDict.split(datas)

        model = params.model

        id = params.id or False
        ids = params.ids or []

        if params.view_type == 'form':
            #TODO: save current record
            ids = (id or []) and [id]

        if id and not ids:
            ids = [id]

        if len(ids):
            from openerp.subcontrollers import actions
            return actions.execute_by_keyword(name, adds=adds, model=model, id=id, ids=ids, report_type='pdf')
        else:
            raise common.message(_("No record selected!"))

    @expose()
    def report(self, **kw):
        return self.do_action('client_print_multi', adds={'Print Screen': {'report_name':'printscreen.list', 
                                                                           'name': _('Print Screen'), 
                                                                           'type':'ir.actions.report.xml'}}, datas=kw)

    @expose()
    def relate(self, **kw):
        return self.action(**kw)

    @expose()
    def action(self, **kw):
        params, data = TinyDict.split(kw)

        action = params.data

        if not action:
            return self.do_action('client_action_multi', datas=kw)

        if not params.selection and not params.id:
            raise common.message(_('You must save this record to use the sidebar button!'))

        from openerp.subcontrollers import actions        
        from openerp.subcontrollers import record

        id = params.id or False
        ids = params.selection or []
        
        if not ids and id:
            ids = [id]

        if not id and ids:
            id = ids[0]

        params.ids = ids
        params.id = id
        
        domain = action.get('domain')
        context = action.get('context')
        
        ctx = {'active_id': id, 'active_ids': ids}
        rec = None
        if domain:
            if not rec: rec = record.Record(params)
            rec.update(ctx)
            domain = rec.expr_eval(domain, rec)
            
            action['domain'] = domain
            
        if context:
            if not rec: rec = record.Record(params)
            rec.update(ctx)
            context = rec.expr_eval(context, rec)
            
            action['context'] = context

        return actions.execute(action, model=params.model, id=id, ids=ids, report_type='pdf')

    @expose()
    def dashlet(self, **kw):
        params, data = TinyDict.split(kw)
        current = params.chain_get(str(params.source) or '') or params

        return self.create(current)
    
    @expose('json')
    def on_change(self, **kw):
        
        data = kw.copy()
        
        callback = data.pop('_terp_callback')
        caller = data.pop('_terp_caller')
        model = data.pop('_terp_model')
        context = data.pop('_terp_context')

        try:
            context = eval(context) # convert to python dict
        except:
            context = {}
        
        match = re.match('^(.*?)\((.*)\)$', callback)
        
        if not match:
            raise common.error(_('Application Error!'), _('Wrong on_change trigger: %s') % callback)
        
        for k, v in data.items():
            try:
                data[k] = eval(v)
            except:
                pass

        result = {}

        prefix = ''
        if '/' in caller:
            prefix = caller.rsplit('/', 1)[0]

        ctx = TinyForm(**kw).to_python()
        pctx = ctx

        if prefix:
            ctx = ctx.chain_get(prefix)

            if '/' in prefix:
                pprefix = prefix.rsplit('/', 1)[0]
                pctx = pctx.chain_get(pprefix)

        ctx2 = rpc.session.context.copy()
        ctx2.update(context or {})

        ctx['parent'] = pctx
        ctx['context'] = ctx2

        func_name = match.group(1)
        arg_names = [n.strip() for n in match.group(2).split(',')]

        ctx_dict = dict(**ctx)
        args = [tools.expr_eval(arg, ctx_dict) for arg in arg_names]

        proxy = rpc.RPCProxy(model)

        ids = ctx.id and [ctx.id] or []

        try:
            response = getattr(proxy, func_name)(ids, *args)
        except Exception, e:
            return dict(error=ustr(e))

        if 'value' not in response:
            response['value'] = {}

        result.update(response)
        
        # apply validators (transform values from python)
        values = result['value']
        values2 = {}
        for k, v in values.items():
            key = ((prefix or '') and prefix + '/') + k

            if key in data:
                values2[k] = data[key]
                values2[k]['value'] = v
            else:
                values2[k] = {'value': v}

        values = TinyForm(**values2).from_python().make_plain()

        # get name of m2o and reference fields
        for k, v in values2.items():
            kind = v.get('type')
            relation = v.get('relation')
            
            if relation and kind in ('many2one', 'reference') and values.get(k):
                values[k] = [values[k], tw.many2one.get_name(relation, values[k])]

        result['values'] = values

        # convert domains in string to prevent them being converted in JSON
        if 'domain' in result:
            for k in result['domain']:
                result['domain'][k] = ustr(result['domain'][k])

        return result

    @expose('json')
    def get_context_menu(self, model, field, kind="char", relation=None, value=None):

        defaults = []
        actions = []
        relates = []

        defaults = [{'text': 'Set to default value', 'action': "set_to_default('%s', '%s')" % (field, model)},
                    {'text': 'Set as default', 'action': "set_as_default('%s', '%s')"  % (field, model)}]

        if kind=='many2one':

            act = (value or None) and "javascript: void(0)"

            actions = [{'text': 'Action', 'action': act and "do_action('%s', '%s')" %(field, relation)},
                       {'text': 'Report', 'action': act and "do_print('%s', '%s')" %(field, relation)}]

            res = rpc.RPCProxy('ir.values').get('action', 'client_action_relate', [(relation, False)], False, rpc.session.context)
            res = [x[2] for x in res]

            for x in res:
                act = (value or None) and "javascript: void(0)"
                x['string'] = x['name']
                relates += [{'text': '... '+x['name'], 
                             'action': act and "do_relate(%s, '%s', '%s', this)" %(x['id'], field, relation), 
                             'data': "%s"%str(x)}]

        return dict(defaults=defaults, actions=actions, relates=relates)

    @expose('json')
    def get_default_value(self, model, field):

        field = field.split('/')[-1]

        res = rpc.RPCProxy(model).default_get([field])
        value = res.get(field)

        return dict(value=value)

    def del_notebook_cookies(self):
        names = cherrypy.request.simple_cookie.keys()

        for n in names:
            if n.endswith('_notebookTGTabber'):
                cherrypy.response.simple_cookie[n] = 0
                
    @expose('json')
    def change_default_get(self, **kw):
        params, data = TinyDict.split(kw)

        ctx = rpc.session.context.copy()
        ctx.update(params.context or {})

        model = params.model
        field = params.caller.split('/')[-1]
        value = params.value or False

        proxy = rpc.RPCProxy('ir.values')
        values = proxy.get('default', '%s=%s' % (field, value), [(model, False)], False, ctx)
        
        data = {}
        for index, fname, value in values:
            data[fname] = value
       
        return dict(values=data)
# vim: ts=4 sts=4 sw=4 si et
                

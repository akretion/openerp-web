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
# -   All names, links and logos of Tiny, OpenERP and Axelor must be
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
import cherrypy
from openerp.controllers import SecuredController, unsecured, actions, login as tiny_login, form
from openerp.utils import rpc, cache, TinyDict

from openobject.tools import url, expose, redirect


def _cp_on_error():

    errorpage = cherrypy.request.pool.get_controller("/openerp/errorpage")
    message = errorpage.render()
    cherrypy.response.status = 500
    cherrypy.response.body = [message]

cherrypy.config.update({'request.error_response': _cp_on_error})

class Root(SecuredController):

    _cp_path = "/openerp"

    @expose()
    def index(self, next=None):
        """Index page, loads the view defined by `action_id`.
        """
        arguments = {}
        if next: arguments = {'next': next}
        else:
            user_action_id = rpc.RPCProxy("res.users").read([rpc.session.uid], ['action_id'], rpc.session.context)[0]['action_id']
            if user_action_id:
                arguments = {'next': '/openerp/home'}
        
        raise redirect("/openerp/menu", **arguments)
    
    @expose()
    def home(self):
        user_action_id = rpc.RPCProxy("res.users").read([rpc.session.uid], ['action_id'], rpc.session.context)[0]['action_id']
        from openerp import controllers
        return controllers.actions.execute_by_id(user_action_id[0])
    
    @expose(content_type='application/octet-stream')
    def report(self, report_name=None, **kw):
        import actions
        return actions.execute_report(report_name, **TinyDict(**kw))
    
    @expose()
    def custom_action(self, action):
        menu_ids = rpc.RPCProxy('ir.ui.menu').search(
                [('id', '=', int(action))], 0, 0, 0, rpc.session.context)

        return actions.execute_by_keyword(
                'tree_but_open', model='ir.ui.menu', id=menu_ids[0], ids=menu_ids,
                context=rpc.session.context, report_type='pdf')

    @expose()
    def info(self):
        return """
    <html>
    <head></head>
    <body>
        <div align="center" style="padding: 50px;">
            <img border="0" src="%s"></img>
        </div>
    </body>
    </html>
    """ % (url("/openerp/static/images/loading.gif"))

    @expose(template="/openerp/controllers/templates/index.mako")
    def menu(self, active=None, next=None):
        from openerp.widgets import tree_view
        
        try:
            id = int(active)
        except:
            id = False
            form.Form().reset_notebooks()
        ctx = rpc.session.context.copy()
        proxy = rpc.RPCProxy("ir.ui.menu")
        ids = proxy.search([('parent_id', '=', False)], 0, 0, 0, ctx)
        parents = proxy.read(ids, ['name'], ctx)
                
        if not id and ids:
            id = ids[0]
            
        for parent in parents:
            if parent['id'] == id:
                parent['active'] = 'active'
            parent['url'] = url('/openerp/menu', active=parent['id'], next=url('/openerp/custom_action', action=parent['id']))
        
        tools = []
        if next: 
            ids = proxy.search([('parent_id', '=', id)], 0, 0, 0, ctx)
            tools = proxy.read(ids, ['name', 'action'], ctx)
            view = cache.fields_view_get('ir.ui.menu', 1, 'tree', {})
            fields = cache.fields_get(view['model'], False, ctx)
            
            for tool in tools:
                tid = tool['id']
                tool['tree'] = tree = tree_view.ViewTree(view, 'ir.ui.menu', tid,
                                        domain=[('parent_id', '=', tid)],
                                        context=ctx, action="/openerp/tree/action", fields=fields)
                tree._name = "tree_%s" %(tid)
                tree.tree.onselection = None
                tree.tree.onheaderclick = None
                tree.tree.showheaders = 0

        return dict(parents=parents, tools=tools, load_content=(next and next or ''))

    @expose(allow_json=True)
    @unsecured
    def login(self, db=None, user=None, password=None, style=None, location=None, **kw):

        location = url(location or '/', kw or {})

        if db and user and user.startswith("anonymous"):
            if rpc.session.login(db, user, password):
                raise redirect(location)

        if cherrypy.request.params.get('tg_format') == 'json':
            if rpc.session.login(db, user, password) > 0:
                return dict(result=1)
            return dict(result=0)

        if style in ('ajax', 'ajax_small'):
            return dict(db=db, user=user, password=password, location=location,
                    style=style, cp_template="/openerp/controllers/templates/login_ajax.mako")

        return tiny_login(target=location, db=db, user=user, password=password, action="login")

    @expose()
    @unsecured
    def logout(self):
        """ Logout method, will terminate the current session.
        """
        rpc.session.logout()
        raise redirect('/openerp')

    @expose(template="/openerp/controllers/templates/about.mako")
    @unsecured
    def about(self):
        from openobject import release
        version = _("Version %s") % (release.version,)
        return dict(version=version)
    
    @expose()
    def blank(self):
        return ''


# vim: ts=4 sts=4 sw=4 si et

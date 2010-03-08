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
import cherrypy
from openerp.controllers import SecuredController, unsecured, login as tiny_login
from openerp.utils import rpc, cache

from openobject.tools import url, expose, redirect


def _cp_on_error():
    
    errorpage = cherrypy.request.pool.get_controller("/errorpage")
    message = errorpage.render()
    cherrypy.response.status = 500
    #cherrypy.response.headers['Content-Type'] = 'text/html'
    cherrypy.response.body = [message]
    
cherrypy.config.update({'request.error_response': _cp_on_error})

class Root(SecuredController):

    _cp_path = "/"

    @expose()
    def index(self):
        """Index page, loads the view defined by `action_id`.
        """
        raise redirect("/menu")
    
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
    
    @expose(template="templates/menu.mako")
    def menu(self, active=None, **kw):
        
        from openerp.utils import icons
        from openerp.widgets import tree_view
        
        try:
            id = int(active)
        except:
            id = False
        
        ctx = rpc.session.context.copy()
        proxy = rpc.RPCProxy("ir.ui.menu")

        ids = proxy.search([('parent_id', '=', False)], 0, 0, 0, ctx)
        parents = proxy.read(ids, ['name', 'icon'], ctx)

        if not id and ids:
            id = ids[0]
            
        ids = proxy.search([('parent_id', '=', id)], 0, 0, 0, ctx)
        tools = proxy.read(ids, ['name', 'icon'], ctx)
        
        view = cache.fields_view_get('ir.ui.menu', 1, 'tree', {})

        for tool in tools:
            tid = tool['id']
            tool['icon'] = icons.get_icon(tool['icon'])
            tool['tree'] = tree = tree_view.ViewTree(view, 'ir.ui.menu', tid, 
                                    domain=[('parent_id', '=', tid)], 
                                    context=ctx, action="/tree/action")
            tree._name = "tree_%s" %(tid)
            tree.tree.onselection = None
            tree.tree.onheaderclick = None
            tree.tree.showheaders = 0
            tree.tree.linktarget = "'appFrame'"

        return dict(parents=parents, tools=tools)

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
                    style=style, cp_template="templates/login_ajax.mako")

        return tiny_login(target=location, db=db, user=user, password=password, action="login")

    @expose()
    @unsecured
    def logout(self):
        """ Logout method, will terminate the current session.
        """
        rpc.session.logout()
        raise redirect('/')

    @expose(template="templates/about.mako")
    @unsecured
    def about(self):
        from openobject import release
        version = _("Version %s") % (release.version,)
        return dict(version=version)


# vim: ts=4 sts=4 sw=4 si et


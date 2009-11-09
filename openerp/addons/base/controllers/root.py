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

import os
import re

import cherrypy

from openerp import tools

from openerp.tools import url
from openerp.tools import rpc
from openerp.tools import cache
from openerp.tools import common
from openerp.tools import expose
from openerp.tools import redirect
from openerp.tools import find_resource

from openerp.controllers import SecuredController, unsecured
from openerp.controllers import login as tiny_login


def _cp_on_error():
    errorpage = cherrypy.request.app.root.errorpage
    message = errorpage.render()
    cherrypy.response.status = 500
    #cherrypy.response.headers['Content-Type'] = 'text/html'
    cherrypy.response.body = [message]

class Root(SecuredController):

    _cp_config = {'request.error_response': _cp_on_error}
    _cp_path = "/"

    def user_action(self, id='action_id'):
        """Perform default user action.

        @param id: `action_id` or `menu_id`
        """

        proxy = rpc.RPCProxy("res.users")
        act_id = proxy.read([rpc.session.uid], [id, 'name'], rpc.session.context)
        
        if not act_id[0][id]:
            common.warning(_('You can not log into the system!\nAsk the administrator to verify\nyou have an action defined for your user.'), _('Access Denied!'))
            rpc.session.logout()
            raise redirect('/');

        act_id = act_id[0][id][0]
        
        import actions
        return actions.execute_by_id(act_id)

    @expose(template="templates/index.mako")
    def index(self):
        """Index page, loads the view defined by `action_id`.
        """
        #return self.user_action('action_id')
        return dict()
        
    @expose()
    def menu(self):
        """Main menu page, loads the view defined by `menu_id`.
        """
        return self.user_action('menu_id')

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
    def get_logo(self):
        
        comp_url = cherrypy.request.app.config['openerp-web'].get('company.url', None)

        res="""<img src="%(src)s" alt="%(alt)s" border="0" width="200px" height="60px" usemap="#logo_map"/>
                    <map name="logo_map">
                        <area shape="rect" coords="102,42,124,56" href="http://openerp.com" target="_blank"/>
                        <area shape="rect" coords="145,42,184,56" href="http://axelor.com" target="_blank"/>
                    </map>"""%({
                        'alt': 'OpenERP',
                        'src': tools.url('/static/images/openerp_big.png')
                    })

        if os.path.exists(find_resource("openerp", "static/images/company_logo.png")):
            if comp_url:
                res = """   <a href='"""+comp_url+"""' target='_blank'>
                                <img src="%(src)s" alt="" border="0" width="205px" height="58px"/>
                            </a> """
            else:
                 res = """<img src="%(src)s" alt="" border="0" width="205px" height="58px"/>"""

        return res % ({'src': tools.url('/static/images/company_logo.png')})

    @expose()
    @unsecured
    def developped_by(self):
        comp_url = cherrypy.request.app.config['openerp-web'].get('company.url', None)

        res="""<img src="%(src)s" border="0" width="200" height="60" alt="%(alt)s" usemap="#devby_map"/>
                    <map name="devby_map">
                        <area shape="rect" coords="0,20,100,60" href="http://axelor.com" target="_blank"/>
                        <area shape="rect" coords="120,20,200,60" href="http://openerp.com" target="_blank"/>
                    </map>"""%(dict(alt=_('Developped by Axelor and Tiny'), src=tools.url('/static/images/developped_by.png')))

        if os.path.exists(find_resource("openerp", "static/images/company_logo.png")):
            if comp_url:
                res = """   <a href='"""+comp_url+"""' target='_blank'>
                                <img src="%(src)s" alt="" border="0" width="205px" height="58px"/>
                            </a> """
            else:
                 res = """<img src="%(src)s" alt="" border="0" width="205px" height="58px"/>"""
        return res % (dict(src=tools.url("/static/images/company_logo.png")))

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
        from openerp import release
        version = _("Version %s") % (release.version,)
        return dict(version=version)
    
    profile = profile.profiler


# vim: ts=4 sts=4 sw=4 si et


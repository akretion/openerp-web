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

"""
This module implementes search view for a tiny model. Currently it simply displays
list view of the given model.

@todo: implement read search window
"""
import cherrypy

from turbogears import expose
from turbogears import widgets
from turbogears import controllers

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from tinyerp import tools
from tinyerp import widgets as tw
from tinyerp.tinyres import TinyResource
from tinyerp import widgets_search as tws

class Search(controllers.Controller, TinyResource):

    def __init__(self):
        pass

    @staticmethod
    def create(model, ids=[], view_ids=[], domain=[], context={}):
        """Create a new instance of search form.

        @param model: the model
        @param ids: record ids
        @param view_ids: view ids
        @param view_mode: view mode
        @param domain: the domain
        @param context: the context
        """
        search = Search()

        search.proxy = rpc.RPCProxy(model)

        search.model = model
        search.ids = ids
        search.view_ids = view_ids
        search.domain = domain
        search.context = context
        search.view_form = search.proxy.fields_view_get({}, 'form', {})
        search.view_tree = search.proxy.fields_view_get({}, 'tree', {})

        search.state = '' #TODO: maintain states
        search.form = {}
        search.form = tws.search_form.Form(prefix='', model=model, view=search.view_form, domain=domain, context=context)
        search.list_view = tw.list.List(model,view=search.view_tree, domain=domain, ids=ids, context=context)

        return search


    @expose(template="tinyerp.modules.gui.templates.search")
    def view(self):

        return dict(form=self.form,
                    list_view = self.list_view,
                    model=self.model,
                    ids=self.ids,
                    view_ids=self.view_ids,
                    domain=self.domain,
                    context=self.context,
                    state=self.state)
    @expose()
    def action(self, terp_model,
                     terp_ids=[],
                     terp_domain=[],
                     terp_view_ids=[],
                     terp_view_mode=['form', 'tree'],
                     terp_view_mode2=['form', 'tree'],
                     terp_context={},
                     terp_action="save",
                     terp_state=None,
                     *args,
                     **kw):
        """Form action controller, performs either of the 'new', 'save',
        'delete', 'edit', 'search', 'button' actions.

        @param terp_model: the model
        @param terp_ids: result_ids
        @param terp_domain: the domain
        @param terp_view_ids: view ids
        @param terp_view_mode: the view mode
        @param terp_view_mode2: the source view mode
        @param terp_context: the local context
        @param terp_action: the action
        @param terp_state: the state
        @param data: the data

        @return: view of the form or search controller
        """

        action = terp_action
        model = terp_model
        state = terp_state

        ids = (terp_ids or []) and eval(terp_ids)
        domain = (terp_domain or []) and eval(terp_domain)
        context = (terp_context or {}) and eval(terp_context)
        view_ids = (terp_view_ids or []) and eval(terp_view_ids)
        #view_mode = (terp_view_mode or ['form', 'tree']) and eval(terp_view_mode)
        #view_mode2 = (terp_view_mode2 or ['form', 'tree']) and eval(terp_view_mode2)


        def getSearchString(name,type,value):
            if value:

                if type == 'many2many' or type == 'one2many' or type =='many2one' or type=='char':
                    return name,'ilike',value
                elif type== 'float' or type == 'integer' or type == 'datetime' or type=='date' or type=='time':
                    if value[0] and value[1]:
                        return [(name,'>=',value[0]),(name,'<=',value[1])]
                    elif value[0]:
                        return name,'>=',value[0]
                    elif value[1]:
                        return name,'<=',value[1]

                    return None

                elif type=='boolen' or type=='selection':
                    return name,'=',value
            return None

        if action == 'Ok':
            pass

        elif action == 'Find':
            ids = None
            fields_type = None
            if cherrypy.session.has_key('field_type'):
                fields_type = cherrypy.session['field_type']
            search_list = []

            if fields_type:
                for n,v in fields_type.items():
                    t = getSearchString(n,v,kw[n])
                    if t:
                        if type(t) == type([]):
                            search_list += t
                        else:
                            search_list += [t]

            if search_list:
                proxy = rpc.RPCProxy(model)
                try:
                    l = int(kw.get('limit','80'))
                    o = int(kw.get('offset','0'))
                except:
                    l = 80
                    o = 0

                ids = proxy.search(search_list,0,l)

            search = Search.create(model=model,
                           ids=ids,
                           view_ids=view_ids,
                           domain=domain,
                           context=context)
            return search.view()


        elif action == 'Cancel':
            pass

        else:
            raise "Invalid action..."

        return search.view()


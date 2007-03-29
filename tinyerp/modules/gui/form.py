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
This module implementes view for a tiny model having

    view_type = 'form'
    view_mode = 'form,tree'
"""

import xml.dom.minidom

from elementtree import ElementTree as ET

from turbogears import expose
from turbogears import widgets

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from tinyerp import tools
from tinyerp import widgets as tw

@expose(template="tinyerp.modules.gui.templates.form")
def create(model, ids=None, view_ids=[], view_mode=['form', 'tree'], domain=[], context={}):
    """Create view for the given model.

    @param view_id: view id
    @param model: the model
    @param ids: record ids
    @param domain: the domain
    @param view_ids: view ids
    @param context: the context

    @return: view of the model (XHTML)
    """

    screen = tw.screen.Screen(prefix='', model=model, ids=ids, view_ids=view_ids, view_mode=view_mode, domain=domain, context=context)

    return dict(screen=screen, model=model, ids=ids, view_ids=view_ids, view_mode=view_mode, domain=domain, context=context, state='')

def make_dict(data):
    """Generates a valid dictionary from the given data to be used with TinyERP.
    """
    res = {}
    for name, value in data.items():
        names = name.split('/')

        if len(names) > 1:
            res.setdefault(names[0], {}).update({"/".join(names[1:]): value})
        else:
            res[name] = value or False

    for k, v in res.items():
        if type(v) == type({}):
            #res[k] = make_dict(v)

            id = 0
            if '__id' in v:
                id = int(v.pop('__id'))

            res[k] = [(id and 1, id, make_dict(v))]

    return res

@expose()
def handler(root, terp_model,
                  terp_ids=[],
                  terp_domain=[],
                  terp_view_ids=[],
                  terp_view_mode=['form', 'tree'],
                  terp_context={},
                  terp_action="save",
                  terp_state=None,
                  terp_cview='form',
                  terp_rview='form',
                  **data):
    """Form handler, performs either of the 'new', 'save', 'delete', 'edit', 'search', 'button'
    action.

    @param terp_model: the model
    @param terp_ids: result_ids
    @param terp_domain: the domain
    @param terp_view_ids: view ids
    @param terp_view_mode: the view mode
    @param terp_context: the local context
    @param terp_action: the action
    @param terp_state: the state
    @param terp_cview: current view_type
    @param terp_rview: return view_type
    @param data: the data

    @rtype: str (mostly XHTML)
    @return: a form or search window
    """

    action = terp_action
    model = terp_model
    state = terp_state
    current_view = terp_cview
    return_view = terp_rview

    ids = (terp_ids or []) and eval(terp_ids)
    domain = (terp_domain or []) and eval(terp_domain)
    context = (terp_context or {}) and eval(terp_context)
    view_ids = (terp_view_ids or []) and eval(terp_view_ids)
    view_mode = (terp_view_mode or ['form', 'tree']) and eval(terp_view_mode)

    data = make_dict(data)

    if action == 'new':
        return create(model=model, ids=[], view_ids=view_ids, view_mode=view_mode, domain=domain, context=context)

    elif action == 'save':
        try:
            if not ids:
                proxy = rpc.RPCProxy(model)
                res = proxy.create(data, context)
                ids = [int(res)]
            else:
                proxy = rpc.RPCProxy(model)
                res = proxy.write(ids, data, context)
        except Exception, e:
            raise e

        return create(model=model, ids=ids, view_ids=view_ids, view_mode=view_mode, domain=domain, context=context)

    elif action == 'delete':
        try:
            proxy = rpc.RPCProxy(model)
            res = proxy.unlink(ids)
        except Exception, e:
            raise e

        return create(model=model, ids=[], view_ids=view_ids, view_mode=view_mode, domain=domain, context=context)

    elif action == 'edit':
        #TODO: open record
        pass

    elif action == 'button':
        #TODO: perform button action
        pass

    elif action == 'search':
        #TODO: generate search view
        pass
    else:
        raise "Invalid action..."

    return dict(action=action, data=data)

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

"""This module implementes action methods.

@todo: implement _execute_wizard
@todo: reimplement _execute_report
"""

import time

from turbogears import controllers
from turbogears import expose
from turbogears import redirect

import cherrypy

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from gui.form import Form
from gui.wizard import Wizard

from utils import TinyDict

def _execute_window(view_id, model, res_id=False, domain=None, view_type='form', context={}, mode='form,tree'):
    """Performs `actions.act_window` action.

    @param view_id: view id
    @param model: a model for which the action should be performed
    @param res_id: res id
    @param domain: domain
    @param view_type: view type, eigther `form` or `tree`
    @param context: the context
    @param mode: view mode, eigther `form,tree` or `tree,form` or None

    @return: view (mostly XHTML code)
    """

    mode = mode.split(',')

    if view_type == 'form':
        params = TinyDict(model=model, ids=res_id, view_mode=mode, view_mode2=mode, view_ids = (view_id and [view_id]) or [], domain=domain, context=context)
        return Form().create(params)

    elif view_type == 'tree':
        return "TREE VIEW: NOT IMPLEMENTED YET!"

    else:
        return "ERROR: INVALID VIEW!"

def _execute_wizard(name, **datas):
    """Executes given wizard with the given data

    @param name: name of the wizard
    @param datas: datas

    @return: wizard view (mostly XHTML code)
    """
    params = TinyDict()
    params.name = name
    params.datas = datas
    params.state = 'init'

    return Wizard().create(params)

def _execute_report(name, **data):
    """Executes a report with the given data, on success returns `application/pdf` data

    @param name: name of the report
    @param data: report data

    @return: JSON object or `application/pdf` data
    """
    datas = data.copy()
    ids = datas['ids']
    del datas['ids']
    if not ids:
        ids =  rpc.session.execute('/object', 'execute', datas['model'], 'search', [])
        if ids == []:
            common.message('Nothing to print!')
            return dict()
        datas['id'] = ids[0]
    try:
        report_id = rpc.session.execute('/report', 'report', name, ids, datas, rpc.session.context)
        state = False
        attempt = 0
        while not state:
            val = rpc.session.execute('/report', 'report_get', report_id)
            state = val['state']
            if not state:
                time.sleep(1)
                attempt += 1
            if attempt>200:
                common.message('Printing aborted, too long delay !')
                return dict()
        #TODO: printer.print_data(val)
        return dict()
    except rpc.RPCException, e:
        #common.error('Error: '+str(e.type), e.message, e.data)
        pass

    return dict()

def _execute(action, **data):
    """Execute the action with the provided data. for internal use only.

    @param action: the action
    @param data: the data

    @return: mostly XHTML code
    """


    if 'type' not in action:
        return

    if action['type']=='ir.actions.act_window':
        for key in ('res_id', 'res_model', 'view_type','view_mode'):
            data[key] = action.get(key, data.get(key, None))

        if not action.get('domain', False):
            action['domain']='[]'

        context = {'active_id': data.get('id', False), 'active_ids': data.get('ids', [])}
        context.update(eval(action.get('context', '{}'), context.copy()))

        a = context.copy()
        a['time'] = time
        domain = tools.expr_eval(action['domain'], a)

        if data.get('domain', False):
            domain.append(data['domain'])

        res = _execute_window(action['view_id'] and action['view_id'][0],
                              data['res_model'],
                              data['res_id'],
                              domain,
                              action['view_type'],
                              context,data['view_mode'])
        return res

    elif action['type']=='ir.actions.wizard':
        if 'window' in data:
            del data['window']
        return _execute_wizard(action['wiz_name'], **data)

    elif action['type']=='ir.actions.report.custom':
        data['report_id'] = action['report_id']
        return _execute_report('custom', **data)

    elif action['type']=='ir.actions.report.xml':
        return _execute_report(action['report_name'], **data)

def execute_by_id(act_id, type=None, **data):
    """Perforns the given action of type `type` with the provided data.

    @param act_id: the action id
    @param type: action type
    @param data: the data

    @return: JSON object or XHTML code
    """
    if type==None:
        res = rpc.session.execute('/object', 'execute', 'ir.actions.actions', 'read', [act_id], ['type'], rpc.session.context)
        if not len(res):
            raise 'ActionNotFound'
        type=res[0]['type']
    res = rpc.session.execute('/object', 'execute', type, 'read', [act_id], False, rpc.session.context)[0]
    return _execute(res, **data)

def execute_by_keyword(keyword, **data):
    """Performs action represented by the given keyword argument with given data.

    @param keyword: action keyword
    @param data: action data

    @return: JSON object or XHTML code
    """

    actions = None
    if 'id' in data:
        try:
            id = data.get('id', False)
            if (id != False): id = int(id)
            actions = rpc.session.execute('/object', 'execute', 'ir.values', 'get', 'action', keyword, [(data['model'], id)], False, rpc.session.context)
            actions = map(lambda x: x[2], actions)
        except rpc.RPCException, e:
            #TODO: common.error('Error: '+str(e.type), e.message, e.data)
            pass

    keyact = {}
    for action in actions:
        keyact[action['name']] = action

    #keyact.update(adds)

    res = common.selection('Select your action', keyact)

    if res:
        return _execute(res[1], **data)
    elif not len(keyact):
        common.message('No action defined!')

    return dict()

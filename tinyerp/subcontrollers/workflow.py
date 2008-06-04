###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt. Ltd. (http://tinyerp.com) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
# Boston, MA  02111-1307, USA.
#
###############################################################################


from turbogears import controllers
from turbogears import expose
from turbogears import widgets
from turbogears import validators
from turbogears import validate
from turbogears import flash

from turbogears import widgets as tg_widgets
from turbogears import validators as tg_validators

import pkg_resources
import cherrypy

from tinyerp import rpc
from tinyerp import cache
from tinyerp import common
from tinyerp import widgets as tw

from form import Form
from tinyerp.utils import TinyDict


rpc.session = rpc.RPCSession('localhost', '8070', 'socket', storage=cherrypy.session)



class State(Form):
    
    path = 'workflow/state'    # mapping from root
    
    @expose(template="tinyerp.subcontrollers.templates.wkf_popup")
    def create(self, params, tg_errors=None):  
              
        params.path = self.path
        params.function = 'create_activity'
        
        if params.id and cherrypy.request.path == '/state/view':
            params.load_counter = 2
        
        form = self.create_form(params, tg_errors)  
        
        field = form.screen.widget.get_widgets_by_name('wkf_id')[0]     
        field.set_value(params.wkf_id or False)
         
        form.hidden_fields = [tg_widgets.HiddenField(name='wkf_id', default=params.wkf_id)]
        vals = getattr(cherrypy.request, 'terp_validators', {})
        vals['wkf_id'] = tw.validators.Int()
                
        return dict(form=form, params=params, show_header_footer=False)

    
    @expose()    
    def edit(self, **kw):
        
        params, data = TinyDict.split(kw)
        if not params.model:
            params.update(kw)
       
        params.view_mode = ['form']
        params.view_type = 'form'
        
        params.editable = True
        
        return self.create(params)
    
    @expose()
    def delete(self,**kw):
        error_msg = None 
        proxy_act = rpc.RPCProxy(kw['model'])
        search_ids = proxy_act.search([('id','=',int(kw['id']))],0,0,0,rpc.session.context)
        datas = proxy_act.read(search_ids,['out_transitions','in_transitions','flow_start'],rpc.session.context)

       
        if datas[0]['flow_start']:
            error_msg = "the activity which start the flow can not be deleted."
        else:
            trs = []
            trs = datas[0]['out_transitions']
            
            for tr in datas[0]['in_transitions']:
                if not trs.__contains__(tr):
                    trs.append(tr)
            
            proxy_tr =  rpc.RPCProxy('workflow.transition')
            res_tr = proxy_tr.unlink(trs)
            
            if res_tr:
                res_act = proxy_act.unlink(int(kw['id']))                

            if not res_act:
                error_msg = 'could not delete'
                
        return dict(error = error_msg)
    
    @expose('json')
    def get_info(self,**kw):
                
        proxy_act = rpc.RPCProxy('workflow.activity')
        search_act = proxy_act.search([('id','=',int(kw['id']))],0,0,0,rpc.session.context)
        data = proxy_act.read(search_act,[],rpc.session.context)
    
        return dict(data=data[0])
    
        



class Connector(Form):
    
    path = 'workflow/connector'    # mapping from root
    
    @expose(template="tinyerp.subcontrollers.templates.wkf_popup")
    def create(self, params, tg_errors=None):
        
        params.path = self.path
        params.function = 'create_transition'
        
        if params.id and cherrypy.request.path == '/connector/view':
            params.load_counter = 2
            
        form = self.create_form(params, tg_errors)
        
        field_act_from = form.screen.widget.get_widgets_by_name('act_from')[0]
        field_act_from.set_value(params.start or False)
        
        field_act_to = form.screen.widget.get_widgets_by_name('act_to')[0]
        field_act_to.set_value(params.end or False)
        
        form.hidden_fields = [tg_widgets.HiddenField(name='act_from', default=params.start)]
        form.hidden_fields = [tg_widgets.HiddenField(name='act_to', default=params.end)]
        vals = getattr(cherrypy.request, 'terp_validators', {})
        vals['act_from'] = tw.validators.Int()
        vals['act_to'] = tw.validators.Int()
        
        return dict(form=form, params=params, show_header_footer=False)
    
            
    @expose()    
    def edit(self, **kw):
        
        params, data = TinyDict.split(kw)
        if not params.model:
            params.update(kw)
        params.view_mode = ['form']
        params.view_type = 'form'
        params.editable = True
        
        return self.create(params)
    
    @expose()
    def delete(self,**kw):
        
        error_msg = None
        proxy_tr = rpc.RPCProxy(kw['model'])
        search_tr = proxy_tr.search([('id','=',int(kw['id']))],0,0,0,rpc.session.context)
        datas = proxy_tr.read(search_tr,['act_from','act_to'],rpc.session.context)        
        
        act_list = []
        act_list.append(datas[0]['act_from'][0])
        if not act_list.__contains__(datas[0]['act_to'][0]):
            act_list.append(datas[0]['act_to'][0]);
        
        
        proxy_act = rpc.RPCProxy('workflow.activity')
        search_act = proxy_act.search([('id','in',act_list)],0,0,0,rpc.session.context)
        data_act = proxy_act.read(search_act,['out_transitions','in_transitions'],rpc.session.context)       
       
        for item in data_act:
            d = []
            d+=item['out_transitions']
            d+=item['in_transitions']
            d.remove(int(kw['id']))  
            if not d:
                error_msg = 'activity can not be made isolated'
                break;
            
        if not error_msg:    
            res_tr = proxy_tr.unlink(search_tr)
        
        return dict(error=error_msg)
    
    @expose('json')
    def save_tr(self,**kw):
        
        proxy_tr = rpc.RPCProxy('workflow.transition')
        id = proxy_tr.create({'act_from':kw['act_from'], 'act_to':kw['act_to']})
        data = proxy_tr.read(id, [], rpc.session.context);
        
        if id>0:
            return dict(flag=True,data=data)
        else:
            return dict(flag=False)
    
    @expose('json')
    def get_info(self,**kw):
                
        proxy_tr = rpc.RPCProxy('workflow.transition')
        search_tr = proxy_tr.search([('id','=',int(kw['id']))],0,0,0,rpc.session.context)
        data = proxy_tr.read(search_tr,[],rpc.session.context)
        
        return dict(data=data[0])
    
    @expose('json')
    def change_ends(self,**kw):     
           
        proxy_tr = rpc.RPCProxy('workflow.transition')
        id = proxy_tr.write([int(kw['id'])], {kw['field']:int(kw['value'])}, rpc.session.context)
        return dict()
        
        
    

        


class Workflow(Form):
    
    path = '/workflow'
    
    @expose(template="tinyerp.subcontrollers.templates.workflow")
    def index(self):
        
        res= rpc.session.login('wkf', 'admin', 'admin')
   
        proxy = rpc.RPCProxy("workflow")
        search_ids = proxy.search([],0,0,0,rpc.session.context)       
        data = proxy.read(search_ids,['name'],rpc.session.context)
        
        return dict(data=data)
   
    @expose()
    def get_wkfl_info(self, **kw):
        
        proxy = rpc.RPCProxy("workflow")
        search_ids = proxy.search([('id','=',int(kw['id']))],0,0,0,rpc.session.context) 
        graph_search = proxy.graph_get(search_ids[0],(200,200,20,20),rpc.session.context) 
         
        nodes = graph_search['node']
        transition = graph_search['transition']
        
        connector = {}
        list_tr = [];
        for item in transition:
            list_tr.append(item)
            connector[item] = {}
            connector[item]['id'] = item
            connector[item]['c'] = transition[item]
            
        proxy_tr = rpc.RPCProxy("workflow.transition")
        search_trs = proxy_tr.search([('id','in',list_tr)],0,0,0,rpc.session.context)
        data_trs = proxy_tr.read(search_trs,['signal','condition'],rpc.session.context)

        for item in data_trs:
            connector[item['id']]['signal'] = item['signal']
            connector[item['id']]['condition'] = item['condition']
        
        proxy_act = rpc.RPCProxy("workflow.activity")
        search_acts = proxy_act.search([('wkf_id','=',int(kw['id']))],0,0,0,rpc.session.context) 
        data_acts = proxy_act.read(search_acts,['flow_start','flow_stop'],rpc.session.context)

        
        dict_acts = {}
        for item in data_acts:
            dict_acts[item['id']] = {}
            dict_acts[item['id']]['flow_start'] = item['flow_start']
            dict_acts[item['id']]['flow_stop'] = item['flow_stop']
        
        for item in nodes:
            nodes[item]['id'] = item
            nodes[item]['flow_start'] = dict_acts[int(item)]['flow_start']
            nodes[item]['flow_stop'] = dict_acts[int(item)]['flow_stop']
        
        return dict(list=nodes,conn=connector)
    
    @expose(template="tinyerp.subcontrollers.templates.wkf_popup")
    def create(self, params, tg_errors=None):

        if params.id and cherrypy.request.path == '/workflow/view':
            params.load_counter = 2
            
        params.path = self.path
        params.function = 'create_wkf'
        
        form = self.create_form(params, tg_errors)
        
        return dict(form=form, params=params, show_header_footer=False)

    @expose()
    def edit(self,**kw):
        
        params, data = TinyDict.split(kw)
        if not params.model:
            params.update(kw)
       
        params.view_mode = ['form']
        params.view_type = 'form'
        
        params.editable = True
        
        return self.create(params)
    
    state = State()
    connector = Connector()



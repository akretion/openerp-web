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

import xml.dom.minidom

import cherrypy

from openerp import rpc
from openerp import tools
from openerp import cache

from sidebar import Sidebar

from interface import Form

import treegrid

class ViewTree(Form):
    
    template = "templates/viewtree.mako"
    params = ['model', 'id', 'ids', 'domain', 'context', 'view_id', 'toolbar']
    members = ['tree', 'sidebar']
    
    def __init__(self, view, model, res_id=False, domain=[], context={}, action=None):
        super(ViewTree, self).__init__(name='view_tree', action=action)

        self.model = view['model']
        self.domain2 = domain or []
        self.context = context or {}

        self.domain = []
        
        self.field_parent = view.get("field_parent") or None

        if self.field_parent:
            self.domain = domain

        self.view = view
        self.view_id = view['view_id']

        proxy = rpc.RPCProxy(self.model)

        ctx = self.context.copy();
        ctx.update(rpc.session.context)

        fields = cache.fields_get(self.model, False, ctx)
        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))

        root = dom.childNodes[0]
        attrs = tools.node_attributes(root)
        self.string = attrs.get('string', 'Unknown')
        self.toolbar = attrs.get('toolbar', False)

        ids = []
        id = res_id

        if self.toolbar:
            ids = proxy.search(self.domain2, 0, 0, 0, ctx)
            self.toolbar = proxy.read(ids, ['name', 'icon'], ctx)

            if not id and ids: 
                id = ids[0]

            if id: 
                ids = proxy.read([id], [self.field_parent])[0][self.field_parent]
        elif not ids:
            ids = proxy.search(domain, 0, 0, 0, ctx)

        self.headers = []
        self.parse(root, fields)

        self.tree = treegrid.TreeGrid(name="tree", 
                                      model=self.model, 
                                      headers=self.headers, 
                                      url="/tree/data", 
                                      ids=ids or 0,
                                      domain=self.domain, 
                                      context=self.context, 
                                      field_parent=self.field_parent)
        self.id = id
        self.ids = ids

        #register callbacks
        self.tree.onselection = "onSelection"
        self.tree.onheaderclick = "onHeaderClick"
        
        toolbar = {}
        for item, value in view.get('toolbar', {}).items():
            if value: toolbar[item] = value
            
        self.sidebar = Sidebar(self.model, toolbar, True, True, context=self.context)

        if self.context and '_view_name' in self.context:
            self.string = self.context.pop('_view_name')
            
        self.children = [self.tree, self.sidebar] + self.hidden_fields
        
    def parse(self, root, fields=None):

        for node in root.childNodes:

            if not node.nodeType==node.ELEMENT_NODE:
                continue

            attrs = tools.node_attributes(node)

            field = fields.get(attrs['name'])
            field.update(attrs)

            self.headers += [field]
            
# vim: ts=4 sts=4 sw=4 si et


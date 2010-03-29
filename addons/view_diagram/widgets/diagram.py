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

import time
import math
import copy
import locale
import xml.dom.minidom

import cherrypy

from openobject import tools

from openobject.i18n import format
from openobject.widgets import CSSLink, JSLink

from openerp.utils import rpc
from openerp.utils import icons
from openerp.utils import common
from openerp.utils import expr_eval
from openerp.utils import node_attributes


from openerp.widgets import TinyWidget
from openerp.widgets import TinyInputWidget
from openerp.widgets import ConcurrencyInfo

from openerp.widgets import get_widget
from openerp.widgets import register_widget


class Diagram(TinyWidget):
    
    template = "templates/diagram.mako"
    member_widgets = []
    
    params = ['dia_id', 'node', 'connector', 'src_node', 'des_node', 'node_flds', 'conn_flds', 'bgcolor', 'shapes']
    
    pager = None
    dia_id = None
    node = ''
    connector = ''
    src_node = ''
    des_node = ''
    node_flds = {}
    conn_flds = []
    bgcolor = {}
    shapes = {}
    
    css = [CSSLink("view_diagram", 'css/graph.css')]
    javascript = [JSLink("view_diagram", 'javascript/draw2d/wz_jsgraphics.js'),
                  JSLink("view_diagram", 'javascript/draw2d/mootools.js'),
                  JSLink("view_diagram", 'javascript/draw2d/moocanvas.js'),
                  JSLink("view_diagram", 'javascript/draw2d/draw2d.js'),
                  JSLink("view_diagram", 'javascript/connector.js'),
                  JSLink("view_diagram", 'javascript/conn_anchor.js'),
                  JSLink("view_diagram", 'javascript/conn_decorator.js'),
                  JSLink("view_diagram", 'javascript/workflow.js'),
                  JSLink("view_diagram", 'javascript/toolbar.js'),
                  JSLink("view_diagram", 'javascript/ports.js'),
                  JSLink("view_diagram", 'javascript/state.js'),
                  JSLink("view_diagram", 'javascript/infobox.js')]
    
    def __init__(self, name, model, view, ids=[], domain=[], context={}, **kw):
        
        super(Diagram, self).__init__(name=name, model=model, ids=ids)
        
        if ids:
            self.dia_id = ids[0]
            
        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))
        root = dom.childNodes[0]
        attrs = node_attributes(root)
        
        self.string = attrs.get('string')
        
        self.parse(root)
        
    def parse(self, root):        
        self.node_flds['visible'] = []
        self.node_flds['invisible'] = []
        
        for node in root.childNodes:
            if node.nodeName == 'node':
                attrs = node_attributes(node)
                self.node = attrs['object']
                self.bgcolor = attrs.get('bgcolor', '')
                self.shapes = attrs.get('shape', '')
#                for color_spec in attrs.get('bgcolor', '').split(';'):
#                    if color_spec:                                            
#                        colour, test = color_spec.split(':')
#                        self.bgcolor[colour] = test
#                
#                for shape_spec in attrs.get('shape', '').split(';'):
#                    if shape_spec:
#                        shape, test = shape_spec.split(':')
#                        self.shapes[shape] = test
                                        
                for fld in node.childNodes:
                    if fld.nodeName == 'field':       
                        attrs = node_attributes(fld)
                        if attrs.has_key('invisible') and attrs['invisible']=='1':
                            self.node_flds['invisible'].append(attrs['name'])
                        else:                  
                            self.node_flds['visible'].append(attrs['name'])
            elif node.nodeName == 'arrow':
                attrs = node_attributes(node)
                self.connector = attrs['object']
                self.src_node = attrs['source']
                self.des_node = attrs['destination']
                
                for fld in node.childNodes:
                    if fld.nodeName == 'field':                        
                        self.conn_flds.append(str(node_attributes(fld)['name']))

# vim: ts=4 sts=4 sw=4 si et
        
                
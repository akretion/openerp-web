###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt. Ltd. (http://openerp.com) All Rights Reserved.
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

import turbogears as tg
import cherrypy

from interface import TinyField
from form import Form
from listgrid import List

from tinyerp import rpc
from tinyerp import cache

from screen import Screen
from tinyerp.utils import TinyDict

import validators as tiny_validators

class M2M(TinyField, tg.widgets.CompoundWidget):
    """many2many widget
    """

    template = "tinyerp.widgets.templates.many2many"
    params = ['relation', 'domain', 'context', 'inline']
    javascript = [tg.widgets.JSLink("tinyerp", "javascript/m2m.js", location=tg.widgets.js_location.bodytop)]

    relation = None
    domain = []
    context = {}
    inline = False

    member_widgets = ['screen']

    def __init__(self, attrs={}):
        super(M2M, self).__init__(attrs)
        tg.widgets.CompoundWidget.__init__(self)

        ids = []
        if hasattr(cherrypy.request, 'terp_params'):
            params = cherrypy.request.terp_params
            self.terp_ids = params.chain_get(params.source)
            
            if self.terp_ids is not None:
                ids = self.terp_ids.ids

        else:
            params = TinyDict()
            params.model = attrs.get('relation', 'model')
            params.ids = attrs.get('value', [])
            params.name = attrs.get('name', '')

        self.model = attrs.get('relation', 'model')
        self.link = attrs.get('link', None)
        
        self.inline = attrs.get('inline')
        self.relation = attrs.get('relation', '')
        self.domain = attrs.get('domain', [])
        self.context = attrs.get('context', {}) or {}

        self.domain  = attrs.get('domain',{})
        
        view = attrs.get('views', {})
        mode = str(attrs.get('mode', 'tree,form')).split(',')

        view_mode = mode
        view_type = mode[0]

        self.switch_to = view_mode[-1]
        if view_type == view_mode[-1]: self.switch_to = view_mode[0]

        if not ids:
            ids = attrs.get('value', [])
        
        id = (ids or None) and ids[0]
        
        pprefix = ''
        if '/' in self.name:
            pprefix = self.name[:self.name.rindex('/')]
       
        current = params.chain_get(self.name)
         
        if not current:
            current = TinyDict()
    
        current.offset = current.offset or 0
        current.limit = current.limit or 20
        current.count = len(ids or [])

        if current.view_mode: view_mode = current.view_mode
        if current.view_type: view_type = current.view_type
        
        if current and params.source == self.name:
            id = current.id

        id = id or None
        
        current.model = self.model
        current.id = id
        
        if isinstance(ids, tuple):
            ids = list(ids)
            
        current.ids = ids
        current.view_mode = view_mode
        current.view_type = view_type
        current.domain = current.domain or []
        current.context = current.context or {}
    
        if current.view_type == 'tree' and self.readonly:
            self.editable = False
        
        self.screen = Screen(current, prefix=self.name, views_preloaded=view, 
                             editable=False, readonly=self.editable, 
                             selectable=2, nolinks=self.link)
        
        self.screen.widget.checkbox_name = False            
#        self.colspan = 4
#        self.nolabel = True

        self.validator = tiny_validators.many2many()

    def set_value(self, value):

        ids = value
        if isinstance(ids, basestring):
            if not ids.startswith('['):
                ids = '[' + ids + ']'
            ids = eval(ids)
            
        self.ids = ids
        
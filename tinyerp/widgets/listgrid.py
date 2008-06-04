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

import time
import math
import locale
import xml.dom.minidom

from turbogears import widgets
from turbogears import i18n

from tinyerp import rpc
from tinyerp import tools
from tinyerp import icons
from tinyerp import format

import form

from pager import Pager

from interface import TinyField
from interface import TinyCompoundWidget

class List(TinyCompoundWidget):

    template = "tinyerp.widgets.templates.listgrid"
    params = ['name', 'data', 'columns', 'headers', 'model', 'selectable', 'editable',
              'pageable', 'selector', 'source', 'offset', 'limit', 'show_links', 'editors', 
              'hiddens', 'edit_inline', 'field_total', 'link', 'checkbox_name']
    
    member_widgets = ['pager', 'children', 'buttons']

    pager = None
    children = []
    field_total = {}
    editors = {}
    hiddens = []
    buttons = []

    edit_inline = None

    data = None
    columns = 0
    headers = None
    model = None
    selectable = False
    editable = False
    pageable = False
    show_links = 1
    source = None
    checkbox_name = True

    css = [widgets.CSSLink('tinyerp', 'css/listgrid.css')]
    javascript = [widgets.JSLink('tinyerp', 'javascript/listgrid.js'),
                  widgets.JSLink('tinyerp', 'javascript/sortablegrid.js'),
                  widgets.JSLink('tinyerp', 'javascript/o2m.js')]

    def __init__(self, name, model, view, ids=[], domain=[], context={}, **kw):

        super(List, self).__init__()
        self.name = name
        self.model = model
        self.ids = ids
        self.context = context or {}
        self.domain = domain or []

        if name.endswith('/'):
            self.name = name[:-1]

        if name != '_terp_list':
            self.source = self.name.replace('/', '/') or None

        self.selectable = kw.get('selectable', 0)
        self.editable = kw.get('editable', False)
        self.pageable = kw.get('pageable', True)

        self.offset = kw.get('offset', 0)
        self.limit = kw.get('limit', 0)
        self.count = kw.get('count', 0)
        self.link = kw.get('nolinks')

        self.selector = None

        if self.selectable == 1:
            self.selector = 'radio'

        if self.selectable == 2:
            self.selector = 'checkbox'

        fields = view['fields']
        dom = xml.dom.minidom.parseString(view['arch'].encode('utf-8'))
        root = dom.childNodes[0]

        attrs = tools.node_attributes(root)
        self.string = attrs.get('string','')

        self.colors = {}
        for color_spec in attrs.get('colors', '').split(';'):
            if color_spec:
                colour, test = color_spec.split(':')
                self.colors[colour] = test

        proxy = rpc.RPCProxy(model)

        if ids == None:
            if self.limit > 0:
                ids = proxy.search(domain, self.offset, self.limit, 0, context)
            else:
                ids = proxy.search(domain, 0, 0, 0, context)

            self.count = proxy.search_count(domain, context)

        data = []
        if len(ids) > 0:

            ctx = rpc.session.context.copy()
            ctx.update(context)

            data = proxy.read(ids, fields.keys(), ctx)

            self.ids = ids

        self.headers, self.hiddens, self.data, self.field_total, self.buttons = self.parse(root, fields, data)

        for k, v in self.field_total.items():
            self.field_total[k][1] = self.do_sum(self.data, k)

        self.columns = len(self.headers)

        self.columns += (self.selectable or 0) and 1
        self.columns += (self.editable or 0) and 2
        self.columns += (self.buttons or 0) and 1

        if self.pageable:
            self.pager = Pager(ids=self.ids, offset=self.offset, limit=self.limit, count=self.count)
            self.pager.name = self.name

        # make editors
        if self.editable and attrs.get('editable') in ('top', 'bottom'):

            for f, fa in self.headers:
                k = fa.get('type', 'char')
                if k not in form.widgets_type:
                    k = 'char'

                fa['prefix'] = '_terp_listfields' + ((self.name != '_terp_list' or '') and '/' + self.name)
                fa['inline'] = True
                self.editors[f] = form.widgets_type[k](fa)

            # generate hidden fields
            for f, fa in self.hiddens:
                k = fa.get('type', 'char')
                if k not in form.widgets_type:
                    k = 'char'

                fa['prefix'] = '_terp_listfields' + ((self.name != '_terp_list' or '') and '/' + self.name)
                self.editors[f] = form.Hidden(fa)

            self.children = self.editors.values()
                    
        # limit the data
        if self.pageable and len(self.data) > self.limit:
            self.data = self.data[self.offset:]
            self.data = self.data[:min(self.limit, len(self.data))]

    def do_sum(self, data, field):
        sum = 0.0

        for d in data:
            value = d[field].value
            sum += value

        attrs = {}
        if data:
            d = data[0]
            attrs = d[field].attrs

        digits = attrs.get('digits', (16,2))
        if isinstance(digits, basestring):
            digits = eval(digits)

        integer, digit = digits
        return format.format_decimal(sum or 0.0, digit)

    def display(self, value=None, **params):

        # set editor values
        if self.editors and self.edit_inline:

            ctx = rpc.session.context.copy()
            ctx.update(self.context)

            fields = [f for f, fa in self.headers]
            fields += [f for f, fa in self.hiddens]

            proxy = rpc.RPCProxy(self.model)

            values = {}
            defaults = {}

            # update values according to domain
            for d in self.domain:
                if d[1] == '=':
                    values[d[0]] = d[2]

            if self.edit_inline > 0:
                values = proxy.read([self.edit_inline], fields, ctx)[0]
            else:
                defaults = proxy.default_get(fields, ctx)

            for k, v in defaults.items():
                values.setdefault(k, v)

            for f in fields:
                if f in values:
                    self.editors[f].set_value(values[f])

        return super(List, self).display(value, **params)

    def parse(self, root, fields, data=[]):
        """Parse the given node to generate valid list headers.

        @param root: the root node of the view
        @param fields: the fields

        @return: an instance of List
        """

        headers = []
        hiddens = []
        buttons = []
        field_total = {}
        values  = [row.copy() for row in data]

        for node in root.childNodes:
            
            if node.nodeName == 'button':
                attrs = tools.node_attributes(node)
                buttons += [Button(attrs)]
                
            elif node.nodeName == 'field':
                attrs = tools.node_attributes(node)

                if 'name' in attrs:

                    name = attrs['name']
                    
                    if attrs.get('widget', False):
                        if attrs['widget']=='one2many_list':
                            attrs['widget']='one2many'
                        attrs['type'] = attrs['widget']
                    
                    try:
                        fields[name].update(attrs)
                    except:
                        print "-"*30,"\n malformed tag for :", attrs
                        print "-"*30
                        raise
                
                    kind = fields[name]['type']

                    if 'sum' in attrs:
                        field_total[name] = [attrs['sum'], 0.0]

                    if kind not in CELLTYPES:
                        kind = 'char'

                    fields[name].update(attrs)

                    invisible = fields[name].get('invisible', False)
                    if isinstance(invisible, basestring):
                        invisible = eval(invisible)

                    if invisible:
                        hiddens += [(name, fields[name])]
                        continue

                    for i, row in enumerate(data):

                        row_value = values[i]

                        cell = CELLTYPES[kind](attrs=fields[name], value=row_value[name])

                        for color, expr in self.colors.items():
                            try:

                                d = row_value.copy()
                                d['current_date'] = time.strftime('%Y-%m-%d')
                                d['time'] = time
                                d['active_id'] = rpc.session.active_id or False

                                if tools.expr_eval(expr, d):
                                    cell.color = color
                                    break
                            except:
                                pass

                        row[name] = cell

                    headers += [(name, fields[name])]

        # generate do_select links
        if self.selectable and headers:
            name, field = headers[0]
            for row in data:
                cell = row[name]

                if self.selectable:
                    cell.link = "javascript: void(0)"
                    cell.onclick = "do_select(%s, '%s'); return false;"%(row['id'], self.name)

        return headers, hiddens, data, field_total, buttons

from tinyerp.stdvars import tg_query

class Char(object):

    def __init__(self, attrs={}, value=False):
        self.attrs = attrs
        self.value = value

        self.text = self.get_text()
        self.link = self.get_link()

        self.color = None
        self.onclick = None

    def get_text(self):
        return self.value or ''

    def get_link(self):
        return None
    
    def get_sortable_text(self):
        """ If returns anything other then None, the return value will be 
        used to sort the listgrid. Useful for localized data.
        """
        return None
    
    def __unicode__(self):
        return ustr(self.text)

    def __str__(self):
        return ustr(self.text)

class M2O(Char):

    def get_text(self):
        if self.value and len(self.value) > 0:
            return self.value[-1]

        return ''

    def get_link(self):
        return tg_query('/form/view', model=self.attrs['relation'], id=(self.value or False) and self.value[0])

class O2M(Char):

    def get_text(self):
        return "(%d)" % len(self.value)

class M2M(Char):

    def get_text(self):
        return "(%d)" % len(self.value)

class Selection(Char):

    def get_text(self):
        if self.value:
            selection = self.attrs['selection']
            for k, v in selection:
                if k == self.value:
                    return v
        return ''

class Float(Char):

    def get_text(self):
        digits = self.attrs.get('digits', (16,2))
        if isinstance(digits, basestring):
            digits = eval(digits)

        integer, digit = digits
        return format.format_decimal(self.value or 0.0, digit)
    
    def get_sortable_text(self):
        return ustr(self.value or '0.0')
        
class FloatTime(Char):

    def get_text(self):
        val = self.value or 0.0
        t = '%02d:%02d' % (math.floor(abs(val)),round(abs(val)%1+0.01,2) * 60)
        if val < 0:
            t = '-' + t
            
        return t

class Int(Char):

    def get_text(self):
        if self.value:
            return int(self.value)

        return 0

class DateTime(Char):
    
    def get_text(self):
        return format.format_datetime(self.value, kind=self.attrs.get('type', 'datetime'))
    
    def get_sortable_text(self):
        return ustr(self.value or '')

class Boolean(Char):

    def get_text(self):
        if int(self.value) == 1:
            return _('Yes')
        else:
            return _('No')
        
class Button(TinyField):
    
    icon = None
    action = None
    record = None
    parent = None
    btype = None
    
    params = ['string', 'icon', 'action', 'record', 'parent', 'btype']
    
    template="""<span xmlns:py="http://purl.org/kid/ns#" py:strip="">
    <button py:if="action and not icon" type="button" py:content="string" py:attrs="attrs"
        onclick="new ListView('${parent}').onButtonClick('${action}', ${record}, '${btype}')"/>
    <img py:if="action and icon" height="16" width="16" class="listImage" src="${icon}" py:attrs="attrs"
        onclick="new ListView('${parent}').onButtonClick('${action}', ${record}, '${btype}')"/>
    <span py:if="not action and not icon">&nbsp;</span>     
</span>"""
    
    def __init__(self, attrs={}):
        super(Button, self).__init__(attrs)
        
        self.states = attrs.get('states', "draft").split(',')
        self.btype = attrs.get('type', "workflow")
        self.icon = attrs.get('icon')
        
        if self.icon:
            self.icon = icons.get_icon(self.icon)

        self.help = self.help or self.string
        
    def has_state(self, data):
        cell = data.get('state')
        return cell and cell.value in self.states
    
    def params_from(self, data):
        
        record = data.get('id')
        action = None

        cell = data.get('state')
        if cell and cell.value in self.states:
            action = self.name
        
        return dict(action=action, record=record)

CELLTYPES = {
        'char':Char,
        'many2one':M2O,
        'datetime':DateTime,
        'date':DateTime,
        'one2many':O2M,
        'many2many':M2M,
        'selection':Selection,
        'float':Float,
        'float_time':FloatTime,
        'integer':Int,
        'boolean' : Boolean
}

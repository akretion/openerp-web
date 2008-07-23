###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
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

import xml
import random

from xml import xpath

# xpath module replaces __builtins__['_'], which breaks TG i18n
import turbogears
turbogears.i18n.tg_gettext.install()

from turbogears import expose
from turbogears import controllers
from turbogears import validators as tg_validators
from turbogears import widgets as tg_widgets

import cherrypy

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common
from tinyerp import cache

from tinyerp.utils import TinyDict

from tinyerp.tinyres import TinyResource

import tinyerp.widgets as tw

from form import Form

class NewField(Form):
    
    path = '/viewed/new_field'    # mapping from root
    
    def create_form(self, params, tg_errors=None):
        form = super(NewField, self).create_form(params, tg_errors)
        
        field = form.screen.widget.get_widgets_by_name('model_id')[0]
        field.set_value(params.model_id or False)
        
        # generate model_id field
        form.hidden_fields = [tg_widgets.HiddenField(name='model_id', default=params.model_id)]
        vals = getattr(cherrypy.request, 'terp_validators', {})
        vals['model_id'] = tw.validators.Int()
                
        return form

    @expose(template="tinyerp.subcontrollers.templates.viewed_new")
    def create(self, params, tg_errors=None):
        
        params.editable = True
        params.model_id = False
        for_model = params.context.get('for_model')
        
        if for_model:
            params.model_id = rpc.RPCProxy('ir.model').search([('model', '=', for_model)])[0]
        
        if not params.id:
            params.context = {'manual' : True}

        form = self.create_form(params, tg_errors)
        
        return dict(form=form, params=params, show_header_footer=False)
    
    @expose()
    def edit(self, for_model, id=False):
        ctx = {'for_model' : for_model}
        return super(NewField, self).edit(model='ir.model.fields', id=id, context=ctx)
   
class NewModel(Form):
    
    path = '/viewed/new_model'    # mapping from root
    
    @expose(template="tinyerp.subcontrollers.templates.viewed_new_model")
    def create(self, params, tg_errors=None):
        
        params.editable = True
        if not params.id:
            params.context = {'manual' : True}

        form = self.create_form(params, tg_errors)
        
        return dict(form=form, params=params, show_header_footer=False)
    
    @expose()
    def edit(self, model=None, id=False, **kw):
        
        params = TinyDict()
        params.model = model
        params.id = id

        id = params.id
        if not id:
            proxy = rpc.RPCProxy('ir.model')
            res = proxy.search([('model', '=', params.model)])
        
            id = (res or False) and res[0]

        return super(NewModel, self).edit(model='ir.model', id=id)

class Preview(Form):
    
    path = '/viewed/preview'    # mapping from root
    
    @expose(template="tinyerp.subcontrollers.templates.viewed_preview")
    def create(self, params, tg_errors=None):
        form = self.create_form(params, tg_errors)
        return dict(form=form, show_header_footer=False)
    
    @expose()
    def show(self, model, view_id, view_type):
        view_id = int(view_id)
        params, data = TinyDict.split({'_terp_model': model,
                                       '_terp_ids' : [], 
                                       '_terp_view_ids' : [view_id],
                                       '_terp_view_mode' : [view_type]})
        return self.create(params)

def _get_xpath(node):

    pn = node.parentNode
    xp = '/' + node.localName

    if pn and pn.localName and pn.localName != 'view':
        xp = _get_xpath(pn) + xp

    nodes = xpath.Evaluate(node.localName, node.parentNode)
    xp += '[%s]' % (nodes.index(node) + 1)

    return xp

def _get_model(node, parent_model):
    
    parents = []
    pnode = node.parentNode
    
    while pnode:
        
        if pnode.localName == 'field':
        
            ch = []
            ch += xpath.Evaluate('./form', pnode)
            ch += xpath.Evaluate('./tree', pnode)
            ch += xpath.Evaluate('./graph', pnode)
            ch += xpath.Evaluate('./calendar', pnode)
        
            if ch:
                parents += [pnode.getAttribute('name')]
                
        pnode = pnode.parentNode
    
    parents.reverse()
    
    for parent in parents:
        
        proxy = rpc.RPCProxy(parent_model)
        field = proxy.fields_get([parent])[parent]
        
        parent_model = field['relation']
        
    return parent_model

def _get_field_attrs(node, parent_model):
    
    if node.localName != 'field':
        return {}
    
    model = _get_model(node, parent_model)
    
    name = node.getAttribute('name')
    proxy = rpc.RPCProxy(model)
    field = proxy.fields_get([name])[name]
    
    return field

class ViewEd(controllers.Controller, TinyResource):
    
    new_field = NewField()
    new_model = NewModel()
    preview = Preview()
    
    @expose(template="tinyerp.subcontrollers.templates.viewed")
    def default(self, view_id):

        try:
            view_id = eval(view_id)
        except:
            pass
        
        if isinstance(view_id, basestring) or not view_id:
            raise common.error(_("Error!"), _("Invalid view id."))
        
        proxy = rpc.RPCProxy('ir.ui.view')
        res = proxy.read(view_id, ['model', 'type'])
        
        model = res['model']
        view_type = res['type']
        
        headers = [{'string' : 'Name', 'name' : 'string', 'type' : 'char'},
                   {'string' : '', 'name': 'add', 'type' : 'image', 'width': 2},
                   {'string' : '', 'name': 'delete', 'type' : 'image', 'width': 2},
                   {'string' : '', 'name': 'edit', 'type' : 'image', 'width': 2},
                   {'string' : '', 'name': 'up', 'type' : 'image', 'width': 2},
                   {'string' : '', 'name': 'down', 'type' : 'image', 'width': 2}]
        
        tree = tw.treegrid.TreeGrid('view_tree', model=model, headers=headers, url='/viewed/data?view_id='+str(view_id))
        tree.showheaders = False
        tree.onselection = 'onSelect'
        tree.onbuttonclick = 'onButtonClick'
        tree.expandall = True

        return dict(view_id=view_id, view_type=view_type, model=model, tree=tree, show_header_footer=False)
    
    def view_get(self, view_id=None):
        
        def _inherit_apply(src, inherit, inherited_id):
            def _find(node, node2):
                # Check if xpath query or normal inherit (with field matching)
                if node2.nodeType==node2.ELEMENT_NODE and node2.localName=='xpath':
                    res = xpath.Evaluate(node2.getAttribute('expr'), node)
                    return res and res[0]
                else:
                    if node.nodeType==node.ELEMENT_NODE and node.localName==node2.localName:
                        res = True
                        for attr in node2.attributes.keys():
                            if attr=='position':
                                continue
                            if node.hasAttribute(attr):
                                if node.getAttribute(attr)==node2.getAttribute(attr):
                                    continue
                            res = False
                        if res:
                            return node
                    for child in node.childNodes:
                        res = _find(child, node2)
                        if res: return res
                return None

            doc_src = xml.dom.minidom.parseString(src.encode('utf-8'))
            doc_dest = xml.dom.minidom.parseString(inherit.encode('utf-8'))
            for node2 in doc_dest.childNodes:
                if not node2.nodeType==node2.ELEMENT_NODE:
                    continue
                node = _find(doc_src, node2)
                if node:
                    vnode = doc_dest.createElement('view')
                    vnode.setAttribute('view_id', str(inherited_id))
                    vnode.appendChild(node2)
                    node.appendChild(vnode)
                else:
                    attrs = ''.join([
                        ' %s="%s"' % (attr, node2.getAttribute(attr)) 
                        for attr in node2.attributes.keys() 
                        if attr != 'position'
                    ])
                    tag = "<%s%s>" % (node2.localName, attrs)
                    raise AttributeError, "Couldn't find tag '%s' in parent view !" % tag
            return doc_src.toxml().replace('\t', '')
        
        proxy = rpc.RPCProxy('ir.ui.view')
        res = proxy.read(view_id)

        def _inherit_apply_rec(result, inherit_id):
            # get all views which inherit from (ie modify) this view
            inherit_ids = proxy.search([('inherit_id', '=', inherit_id)], 0, 0, 'priority')
            inherit_res = proxy.read(inherit_ids, ['arch', 'id'])
            
            for res2 in inherit_res:
                result = _inherit_apply(result, res2['arch'], res2['id'])
                result = _inherit_apply_rec(result, res2['id'])
            
            return result
        
        doc_arch = _inherit_apply_rec(res['arch'], view_id)
        doc_arch = xml.dom.minidom.parseString(doc_arch.encode('utf-8'))
        
        new_doc = xml.dom.getDOMImplementation().createDocument(None, 'view', None)
        new_doc.documentElement.setAttribute('view_id', str(view_id))
        new_doc.documentElement.appendChild(doc_arch.documentElement)
        
        res = {'model': res['model'],
               'view_id' : view_id,
               'view_type': res['type'],
               'arch' : new_doc.toxml().replace('\t', '')}

        return res
    
    def get_node_instance(self, node, model, view_id=False, view_type='form'):
        
        field_attrs = _get_field_attrs(node, parent_model=model)
        
        attrs = tools.node_attributes(node)
        
        view_id = attrs.get('view_id', view_id)
        view_type = attrs.get('view_type', view_type)
        
        attrs['view_id'] = view_id
        attrs['view_type'] = view_type
        
        attrs['__localName__'] = node.localName
        attrs['__id__'] = random.randrange(1, 10000)
        
        attrs.setdefault('name', node.localName)
        
        field_attrs.update(attrs)
        
        return _NODES.get(node.localName, Node)(field_attrs)

    def parse(self, root=None, model=None, view_id=False, view_type='form'):

        result = []
    
        for node in root.childNodes:
            
            if not node.nodeType==node.ELEMENT_NODE:
                continue
            
            attrs = tools.node_attributes(node)
        
            view_id = attrs.get('view_id', view_id)
            view_type = attrs.get('view_type', view_type)
            
            children = []
            
            if node.childNodes:
                children = self.parse(node, model=model, view_id=view_id, view_type=view_type)

            node_instance = self.get_node_instance(node, model=model, view_id=view_id, view_type=view_type)
            node_instance.children = children
            
            result += [node_instance]

        return result
    
    @expose('json')
    def data(self, view_id, **kw):
        view_id = int(view_id)
        
        res = self.view_get(view_id)
        
        model = res['model']
        view_type = res['view_type']
        arch = res['arch']
        
        doc = xml.dom.minidom.parseString(arch.encode('utf-8'))
        result = self.parse(root=doc, model=model, view_id=view_id, view_type=view_type)
        
        records = [rec.get_record() for rec in result]
        
        return dict(records=records)
    
    @expose(template="tinyerp.subcontrollers.templates.viewed_edit")
    def edit(self, view_id, xpath_expr):
        
        view_id = int(view_id)
        
        proxy = rpc.RPCProxy('ir.ui.view')
        res = proxy.read(view_id, ['model', 'arch'])
        
        doc = xml.dom.minidom.parseString(res['arch'].encode('utf-8'))        
        field = xpath.Evaluate(xpath_expr, doc)[0]

        attrs = tools.node_attributes(field)
        editors = []
        
        properties = _PROPERTIES.get(field.localName, [])
        if field.localName == 'field':
            kind = 'char'
            try:
                model = _get_model(field, parent_model=res['model'])
                proxy = rpc.RPCProxy(model)
                attrs2 = proxy.fields_get([attrs['name']])[attrs['name']]

                attrs2.update(attrs)

                if attrs2.get('widget', False):
                    if attrs2['widget']=='one2many_list':
                        attrs2['widget']='one2many'
                    attrs2['type'] = attrs2['widget']

                kind = attrs2.get('type', kind)
            except:
                pass
            properties = _PROPERTIES_FIELDS.get(kind) or properties
        properties = properties[:]
        properties += list(set(attrs.keys()) - set(properties))
        
        for prop in properties:
            if field.localName == 'action' and prop == 'name':
                ed = ActionProperty(prop, attrs.get(prop))
            else:
                ed = get_property_widget(prop, attrs.get(prop))
                
            ed.label = prop
            
            editors += [ed]
            
        return dict(view_id=view_id, xpath_expr=xpath_expr, editors=editors)
    
    @expose(template="tinyerp.subcontrollers.templates.viewed_add")
    def add(self, view_id, xpath_expr):
        view_id = int(view_id)
        
        proxy = rpc.RPCProxy('ir.ui.view')
        res = proxy.read(view_id, ['model', 'arch'])
        
        doc = xml.dom.minidom.parseString(res['arch'].encode('utf-8'))        
        model = res['model']
        
        field_node = xpath.Evaluate(xpath_expr, doc)[0]
        model = _get_model(field_node, parent_model=model)
        
        # get the fields
        proxy = rpc.RPCProxy(model)
        fields = proxy.fields_get().keys()
        
        nodes = _CHILDREN.keys()
        nodes.remove('view')
        
        nodes.sort()
        fields.sort()
        
        positions = [('inside', 'Inside'), ('after', 'After'), ('before', 'Before')]
        if field_node.localName in [k for k,v in _CHILDREN.items() if not v] + ['field']:
            positions = [('after', 'After'), ('before', 'Before'), ('inside', 'Inside')]
        
        return dict(view_id=view_id, xpath_expr=xpath_expr, nodes=nodes, fields=fields, model=model, positions=positions)
    
    @expose('json')
    def create_view(self, view_id=False, xpath_expr=None, **kw):
        
        view_id = int(view_id)
        
        proxy = rpc.RPCProxy('ir.ui.view')
        res = proxy.read(view_id, ['model', 'type', 'arch'])
        
        model = res['model']
        view_type = res['type']
        
        error = None
        record = None
        
        if view_id:
            
            doc = xml.dom.minidom.parseString(res['arch'].encode('utf-8'))
            node = xpath.Evaluate(xpath_expr, doc)[0]
            new_node = doc.createElement('view')
            
            if node.localName == 'field':

                data = {'name' : res['model'] + '.' + str(random.randint(0, 100000)) + '.inherit',
                        'model' : res['model'],
                        'priority' : 16,
                        'type' : view_type,
                        'inherit_id' : view_id}
            
                arch = """<?xml version="1.0"?>
                <field name="%s" position="after">
                </field>""" % (node.getAttribute('name'))
                
                data['arch'] = arch
            
                try:
                    view_id = proxy.create(data)
                    record = self.get_node_instance(new_node, model, view_id, view_type).get_record()
                    node.setAttribute('position', 'after')
                    record['children'] = [self.get_node_instance(node, model, view_id, view_type).get_record()]

                except:
                    error = _("Unable to create inherited view.")
            else:
                error = _("Can't create inherited view here.")
                
        else:
            error = _("Not implemented yet!")
        
        try:
            cache.clear()
        except:
            pass
        
        return dict(record=record, error=error)
    
    @expose('json')
    def remove_view(self, view_id, **kw):
        
        view_id = int(view_id)
        
        if view_id:
            proxy = rpc.RPCProxy('ir.ui.view')
            proxy.unlink(view_id)
        
        try:
            cache.clear()
        except:
            pass
        
        return dict()
    
    @expose('json')
    def save(self, _terp_what, view_id, xpath_expr, **kw):
        
        view_id = int(view_id)
        
        proxy = rpc.RPCProxy('ir.ui.view')
        res = proxy.read(view_id, ['model', 'type', 'arch'])
        
        model = res['model']
        view_type = res['type']
        
        doc = xml.dom.minidom.parseString(res['arch'].encode('utf-8'))
        node = xpath.Evaluate(xpath_expr, doc)[0]

        new_node = None
        record = None

        if _terp_what == "properties":
            
            attrs = tools.node_attributes(node)        
            for attr in attrs:
                node.removeAttribute(attr)
        
            for attr, val in kw.items():
                if val:
                    node.setAttribute(attr, val)
        
        elif _terp_what == "node" and node.parentNode:
            
            new_node = doc.createElement(kw['node'])
            
            if new_node.localName == "field":
                new_node.setAttribute('name', kw.get('name', new_node.localName))
                
            pnode = node.parentNode
            position = kw['position']
            
            try:
                
                if position == 'after':
                    pnode.insertBefore(new_node, node.nextSibling)
                    
                if position == 'before':
                    pnode.insertBefore(new_node, node)
                    
                if position == 'inside':
                    node.appendChild(new_node)
                
            except Exception, e:
                return dict(error=ustr(e))
            
        elif _terp_what == "move":
            
            refNode = None
            try:
                refNode = xpath.Evaluate(kw['xpath_ref'], doc)[0]
            except:
                pass
                            
            pnode = node.parentNode
            newNode = pnode.removeChild(node)

            pnode.insertBefore(newNode, refNode)

        elif _terp_what == "remove":
            pnode = node.parentNode
            pnode.removeChild(node)
        
        if _terp_what != 'remove':
            node_instance = self.get_node_instance(new_node or node, model=model, view_id=view_id, view_type=view_type)
            node_instance.children = self.parse(new_node or node, model, view_id, view_type)
            record = node_instance.get_record()
            
        data = dict(arch=doc.toxml(encoding="utf-8"))
        try:
            res = proxy.write([view_id], data)
        except:
            return dict(error=_("Unable to update the view."))
        
        try:
            cache.clear()
        except:
            pass
        
        return dict(record=record)

class Node(object):
    
    def __init__(self, attrs, children=None):
        self.attrs = attrs or {}
        self.children = children
        
        self.view_id = self.attrs['view_id']
        self.id = self.attrs['__id__']
        
        self.name = self.attrs['name']
        self.localName = self.attrs['__localName__']
        self.string = self.get_text()
        
    def get_text(self):
        return "<%s>" % self.name
    
    def get_record(self):
        items = {'string' : self.string,
                 'name' : self.name,
                 'localName' : self.localName,
                 'view_id' : self.view_id,
                 'delete': '/static/images/stock/gtk-remove.png'}
        
        if self.localName not in ('view'):
            items['add'] = '/static/images/stock/gtk-add.png'
            items['up'] = '/static/images/stock/gtk-go-up.png'
            items['down'] = '/static/images/stock/gtk-go-down.png'
            
        if self.localName not in ('view', 'newline'):
            items['edit'] = '/static/images/stock/gtk-edit.png'

        record = { 'id' : self.id, 'items' : items}
        
        if self.children:
            record['children'] = [c.get_record() for c in self.children]

        return record

class ViewNode(Node):
    
    def get_text(self):
        return '<view view_id="%s">' % self.view_id
    
class FieldNode(Node):
    
    def get_text(self):
        
        if self.attrs.get('type') == 'one2many':
            return '[{%s}]' % self.name
        
        return '[%s]' % self.name
    
class ButtonNode(Node):
    
    def get_text(self):
        return '<button>'
    
class ActionNode(Node):
    
    def get_text(self):
        return '<action>'

_NODES = {
    'view' : ViewNode,
    'field': FieldNode,
    'button' : ButtonNode,
    'action' : ActionNode
}

_PROPERTIES = {
    'field' : ['name', 'string', 'required', 'readonly', 'select', 'domain', 'context', 'nolabel', 'completion', 
               'colspan', 'widget', 'eval', 'ref', 'on_change', 'attrs', 'groups'],
    'form' : ['string', 'col', 'link'],
    'notebook' : ['colspan', 'position', 'groups'],
    'page' : ['string', 'states', 'attrs', 'groups'],
    'group' : ['string', 'col', 'colspan', 'states', 'attrs', 'groups'],
    'image' : ['filename', 'width', 'height', 'groups'],
    'separator' : ['string', 'colspan', 'groups'],
    'label': ['string', 'align', 'colspan', 'groups'],
    'button': ['name', 'string', 'icon', 'type', 'states', 'readonly', 'special', 'target', 'confirm', 'attrs', 'groups'],
    'newline' : [],
    'hpaned': ['position', 'groups'],
    'vpaned': ['position', 'groups'],
    'child1' : ['groups'],
    'child2' : ['groups'],
    'action' : ['name', 'string', 'colspan', 'groups'],
    'tree' : ['string', 'colors', 'editable', 'link'],
    'graph' : ['string', 'type'],
    'calendar' : ['string', 'date_start', 'date_stop', 'date_delay', 'day_length', 'color'],
    'view' : [],
    'properties' : ['groups'],
}

# TODO: valid attributes for each field type
_PROPERTIES_FIELDS = {
    'date': [],
    'time': [],
    'float_time': [],
    'datetime': [],
    'float': [],
    'integer': [],
    'selection': [],
    'char': [],
    'boolean': [],
    'button': [],
    'reference': [],
    'binary': [],
    #'picture': Picture,
    'text': [],
    'text_tag': [],
    'html_tag': [],
    'one2many': [],
    'one2many_form': [],
    'one2many_list': [],
    'many2many': [],
    'many2one': [],
    'email' : [],
    'url' : [],
    'image' : ['name', 'string', 'width', 'height', 'required', 'readonly', 
               'domain', 'context', 'nolabel', 'colspan', 'widget', 'eval',
               'attrs', 'groups']
}

_CHILDREN = {
    'view': ['form', 'tree', 'graph', 'calendar', 'field'],
    'form': ['notebook', 'group', 'field', 'label', 'button', 'image', 'newline', 'separator', 'properties'],
    'tree': ['field'],
    'graph': ['field'],
    'calendar': ['field'],
    'notebook': ['page'],
    'page': ['notebook', 'group', 'field', 'label', 'button', 'image', 'newline', 'separator', 'properties'],
    'group': ['field', 'label', 'button', 'separator', 'newline'],
    'hpaned': ['child1', 'child2'],
    'vpaned': ['child1', 'child2'],
    'child1': ['action'],
    'child2': ['action'],
    'action': [],
    'field': ['form', 'tree', 'graph'],
    'label': [],
    'button' : [],
    'image': [],
    'newline': [],
    'separator': [],
    'properties': [],
}

class SelectProperty(tg_widgets.SingleSelectField):
    
    def __init__(self, name, default=None):
        
        options = [('', 'Not Searchable'),
                   ('1', 'Always Searchable'),
                   ('2', 'Advanced Search')]
        
        super(SelectProperty, self).__init__(name=name, options=options, default=default)
        
class PositionProperty(tg_widgets.SingleSelectField):
    
    def __init__(self, name, default=None):
        
        options = [('', ''),
                   ('after', 'After'),
                   ('before', 'Before'),
                   ('inside', 'Inside'),
                   ('replace', 'Replace')]
        
        super(PositionProperty, self).__init__(name=name, options=options, default=default)        
        
class WidgetProperty(tg_widgets.SingleSelectField):
    
    def __init__(self, name, default=None):
        
        options = [''] + tw.form.widgets_type.keys()
                
        super(WidgetProperty, self).__init__(name=name, options=options, default=default)        
        
class BooleanProperty(tg_widgets.CheckBox):
    
    def __init__(self, name, default=None):
        super(BooleanProperty, self).__init__(name=name, attrs=dict(value=1, checked=default))
        self.field_class = "checkbox"
        
class GroupsProperty(tg_widgets.MultipleSelectField):
    
    def __init__(self, name, default=None):
                
        default = default or ''
        default = default.split(',')
        
        group_ids = rpc.RPCProxy('res.groups').search([])
        groups = rpc.RPCProxy('ir.model.data').search([('res_id', 'in', group_ids ), ('model', '=', 'res.groups')])
        groups = rpc.RPCProxy('ir.model.data').read(groups, ['module', 'res_id', 'name'])
        
        groups_names = rpc.RPCProxy('res.groups').read(group_ids, ['name'])
        names = dict([(n['id'], n['name']) for n in groups_names])
        
        options = [('%s.%s' % (g['module'], g['name']), names[g['res_id']]) for g in groups]
        
        super(GroupsProperty, self).__init__(name=name, options=options, default=default)

class ActionProperty(tw.many2one.M2O):
    
    def __init__(self, name, default=None):
        attrs = dict(name=name, relation='ir.actions.actions')
        super(ActionProperty, self).__init__(attrs)
        self.set_value(default or False)
    
_PROPERTY_WIDGETS = {
    'select' : SelectProperty,
    'required' : BooleanProperty,                                                               
    'readonly' : BooleanProperty,
    'nolabel' : BooleanProperty,
    'completion' : BooleanProperty,
    'widget' : WidgetProperty,
    'groups' : GroupsProperty,
    'position': PositionProperty                                             
}

def get_property_widget(name, value=None):
    wid = _PROPERTY_WIDGETS.get(name, tg_widgets.TextField)
    return wid(name=name, default=value)

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

import cherrypy

from openerp import tools

from openerp.widgets.base import Widget
from openerp.widgets.base import InputWidget


__all__ = ['TinyWidget', 'TinyInputWidget', 'TinyCompoundWidget', 'ConcurrencyInfo']


_attrs_boolean = {
    'select': False,
    'nolabel': False,
    'required': False,
    'readonly': False,
}

def _boolean_attr(attrs, name):

    if name not in _attrs_boolean:
        return attrs.get(name)

    val = attrs.get(name)
    if isinstance(val, basestring) and val.lower() in ('false', 'none', '0'):
        return False
    
    return (attrs.get(name) and True) or _attrs_boolean.get(name)

class _Interface(object):

    params = [
        'colspan',
        'rowspan',
        'string',
        'nolabel',
        'select',
        'required',
        'readonly',
        'help',
        'editable',
        'translatable',
        'visible',
        'inline',
        'name',
        'model',
        'states',
        'callback',
        'change_default',
        'onchange',
        'kind',
    ]

    colspan = 1
    rowspan = 1
    string = None
    nolabel = False
    select = False
    required = False
    readonly = False
    help = None
    editable = True
    translatable = False
    visible = True
    inline = False

    name = None
    model = None
    states = None
    callback = None
    change_default = None
    onchange = 'onChange(this)'
    kind=None
    
    def __init__(self, **attrs):

        prefix = attrs.get('prefix', '')
        self._id = prefix + (prefix and '/' or '') + attrs.get('name', '')

        if isinstance(self.states, basestring):
            self.states = self.states.split(',')

        self.colspan = int(self.colspan)
        self.rowspan = int(self.rowspan)
        
        self.select = _boolean_attr(attrs, 'select')
        self.nolabel = _boolean_attr(attrs, 'nolabel')
        self.required = _boolean_attr(attrs, 'required')
        self.readonly = _boolean_attr(attrs, 'readonly')

        self.visible = True

        try:
            visval = attrs.get('invisible', 'False')
            ctx = attrs.get('context', {})
            self.invisible = eval(visval, {'context': ctx})
        except:
            pass

        self.translatable = attrs.get('translate', False)

        self.set_state(attrs.get('state', 'draft'))

        self.callback = attrs.get('on_change', None)
        self.kind = attrs.get('type', None)

        self.attributes = attrs.get('attrs', {})

    def set_state(self, state):

        if isinstance(self.states, dict) and state in self.states:

            attrs = dict(self.states[state])

            if 'readonly' in attrs:
                self.readonly = attrs['readonly']

            if 'required' in attrs:
                self.required = attrs['required']

            if 'value' in attrs:
                self.default = attrs['value']

class TinyWidget(Widget, _Interface):

    def __new__(cls, **attrs):
        return super(TinyWidget, cls).__new__(cls, **attrs)
    
    def __init__(self, **attrs):

        Widget.__init__(self, **attrs)
        _Interface.__init__(self, **attrs)


class TinyInputWidget(InputWidget, _Interface):
    
    def __new__(cls, **attrs):
        return super(TinyInputWidget, cls).__new__(cls, **attrs)

    def __init__(self, **attrs):
        InputWidget.__init__(self, **attrs)
        _Interface(self, **attrs)

        self._name = self._id
        self._validator = None

    def get_validator(self):

        # required fields are now validated at client side
        #if self._validator:
        #    self._validator.not_empty = (self.required or False) and True
        #elif self.required:
        #    self._validator = tg.validators.NotEmpty()

        return self._validator

    def set_validator(self, value):
        self._validator = value

    validator = property(get_validator, set_validator)

    def get_value(self):
        """Get the value of the field.

        @return: field value
        """
        return self.default

    def set_value(self, value):
        """Set the value of the field.

        @param value: the value
        """
        if isinstance(value, basestring):
            value = ustr(value)

        self.default = value
        
    def get_display_value(self):
        """Get the display value of the field.
        """
        
        try:
            return self.validator.from_python(self.default)
        except:
            pass
        
        return self.get_value()
    
    def update_params(self, d):
        InputWidget.update_params(self, d)

        attrs = d['attrs'] = {}

        attrs['change_default'] = self.change_default or None
        attrs['callback'] = self.callback or None
        attrs['onchange'] = self.onchange

        d['kind'] = self.kind
        d['editable'] = self.editable
        d['inline'] = self.inline

        if self.readonly:
            d.setdefault('css_classes', []).append("readonlyfield")
            attrs['disabled'] = 'disabled'

        if self.required and 'requiredfield' not in d['field_class'].split(' '):
            d.setdefault('css_classes', []).append("requiredfield")

        if self.translatable and 'translatable' not in d['field_class'].split(' '):
            d.setdefault('css_classes', []).append("translatable")

        if hasattr(self, 'error') and self.error:
            d.setdefault('css_classes', []).append("errorfield")


class TinyCompoundWidget(TinyInputWidget):

    def get_widgets_by_name(self, name, kind=tg.widgets.Widget, parent=None):

        result = []
        parent = parent or self

        for wid in parent.children:

            if wid.name == name and isinstance(wid, kind):
                result.append(wid)

            if wid.children:
                result += self.get_widgets_by_name(name, kind=kind, parent=wid)

        return result

    def get_last_update_info(resource, values):
        result = {}
        for item in values:
            result["%s,%s" % (resource, item['id'])] = item.pop('__last_update', '')
        return result

    def _update_concurrency_info(self, resource, records):
        info = getattr(cherrypy.request, 'terp_concurrency_info', {})
        vals = info.setdefault(resource, {})
        for item in records:
            vals[item['id']] = item.pop('__last_update', '')
        cherrypy.request.terp_concurrency_info = info

    def update_params(self, d):
        TinyInputWidget.update_params(self, d)
        d['editable'] = self.editable


class ConcurrencyInfo(TinyCompoundWidget):

    template="""
    % if ids and model in info:
        % for id in ids:
            % if id in info[model]:
                <input type="hidden" name="_terp_concurrency_info" value="('${model},${id}', '${info[model][id]}')"/>
            % endif
        % endfor
    % endif
    """

    params = ['ids', 'model', 'info']

    def __init__(self, model, ids):
        self.ids = ids
        self.model = model

    def _get_concurrency_info(self):
        return getattr(cherrypy.request, 'terp_concurrency_info', {})

    info = property(_get_concurrency_info)

# vim: ts=4 sts=4 sw=4 si et


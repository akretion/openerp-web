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

import re
import cherrypy

from turbogears import validators as tg_validators
from openerp.widgets import validators as tw_validators

def _make_dict(data, is_params=False):
    """If is_params is True then generates a TinyDict otherwise generates a valid
    dictionary from the given data to be used with OpenERP.

    @param data: data in the form of {'a': 1, 'b/x': 1, 'b/y': 2}
    @param is_params: if True generate TinyDict instead of standard dict

    @return: TinyDict or dict
    """

    res = (is_params or {}) and TinyDict()

    for name, value in data.items():

        #XXX: safari 3.0 submits selection field even if no `name` attribute
        if not name:
            continue
        
        if isinstance(name, basestring) and '/' in name:        
            names = name.split('/')
            res.setdefault(names[0], (is_params or {}) and TinyDict()).update({"/".join(names[1:]): value})
        else:
            res[name] = value

    for k, v in res.items():
        if isinstance(v, dict):
            if not is_params and '__id' in v:
                id = v.pop('__id') or 0
                id = int(id)

                values = _make_dict(v, is_params)
                if values:
                    res[k] = [(id and 1, id, values)]

            else:
                res[k] = _make_dict(v, is_params and isinstance(v, TinyDict))

    return res

class TinyDict(dict):
    """A dictionary class that allows accessing it's items as it's attributes.
    It also converts stringified Boolean, None, Number or secuence to python object.
    This class is mainly used by Controllers to get special `_terp_` arguments and
    to generate valid dictionary of data fields from the controller keyword arguments.
    """

    def __init__(self, **kwargs):
        super(TinyDict, self).__init__()
        
        for k, v in kwargs.items():
            if (isinstance(v, dict) and not isinstance(v, TinyDict)):
                v = TinyDict(**v)
            self[k] = v

    def _eval(self, value):
        if not isinstance(value, basestring):
            return value

        pat = re.compile('^(True|False|None|-?\d+(\.\d+)?|\[.*?\]|\(.*?\)|\{.*?\})$', re.M)
        if pat.match(value):
            try:
                return eval(value)
            except:
                pass

        return value

    def __setattr__(self, name, value):
        name = '_terp_%s' % name
        value = self._eval(value)
        
        self[name] = value

    def __getattr__(self, name):
        nm = '_terp_%s' % name
        return self.get(nm, self.get(name, None))
    
    def __setitem__(self, name, value):
        value = self._eval(value)
        super(TinyDict, self).__setitem__(name, value)
        
    def chain_get(self, name, default=None):
        names = re.split('\.|/', ustr(name))
        value = super(TinyDict, self).get(names[0], default)

        for n in names[1:]:
            if isinstance(value, TinyDict):
                value = value.get(n, default)

        return value

    @staticmethod
    def split(kwargs):
        """A helper function to extract special parameters from the given kwargs.

        @param kwargs: dict of keyword arguments

        @rtype: tuple
        @return: tuple of dicts, (TinyDict, dict of data)
        """

        params = TinyDict()
        data = {}

        for n, v in kwargs.items():
            if n.find('_terp_') > -1:
                params[n] = v
            else:
                data[n] = v

        return _make_dict(params, True), _make_dict(data, False)
    
    def make_plain(self, prefix=''):

        res = {}

        def _plain(data, prefix):
            for k, v in data.items():
                if isinstance(v, dict):
                    _plain(v, prefix + k +'/')
                else:
                    res[prefix + k] = v

        _plain(self, prefix)

        return res

    def make_dict(self):
        res = {}
        for k, v in self.items():
            if isinstance(v, TinyDict):
                v = v.make_dict()
            res[k] = v
        return res

_VALIDATORS = {
    'date': lambda *a: tw_validators.DateTime(kind="date"),
    'time': lambda *a: tw_validators.DateTime(kind="time"),  
    'datetime': lambda *a: tw_validators.DateTime(kind="datetime"),
    'float_time': lambda *a: tw_validators.FloatTime(),
    'float': lambda *a: tw_validators.Float(),
    'integer': lambda *a: tw_validators.Int(),
    'selection': lambda *a: tw_validators.Selection(),
    'char': lambda *a: tw_validators.String(),
    'boolean': lambda *a: tw_validators.Bool(),
    'reference': lambda *a: tw_validators.Reference(),
    'binary': lambda *a: tw_validators.Binary(),
    'text': lambda *a: tw_validators.String(),
    'text_tag': lambda *a: tw_validators.String(),
    'many2many': lambda *a: tw_validators.many2many(),
    'many2one': lambda *a: tw_validators.many2one(),
    'email' : lambda *a: tw_validators.Email(),
    'url' : lambda *a: tw_validators.Url(),
	'picture': lambda *a: tw_validators.Picture(),
}

class TinyFormError(tg_validators.Invalid):
    def __init__(self, field, msg, value):
        tg_validators.Invalid.__init__(self, msg, value, state=None, error_list=None, error_dict=None)
        self.field = field
               
class TinyForm(object):
    """An utility class to convert:
    
        1. local form data to the server data (throws exception if any)
        2. server data to the local data
    
    Using validators.
    """

    def __init__(self, **kwargs):
        
        self.data = {}
        for k, v in kwargs.items():
            if '_terp_' not in k:
                try:
                    v = eval(v)
                except:
                    pass
                self.data['_terp_form/' + k] = v
                
    def _convert(self, form=True):
        
        kw = {}
        for name, attrs in self.data.items():
            
            if not isinstance(attrs, dict):
                kw[name] = attrs
                continue
            
            kind = attrs.get('type', 'char')
            value = attrs.get('value')
            
            required = attrs.get('required', False)

            if kind not in _VALIDATORS:
                kind = 'char'
                
            v = _VALIDATORS[kind]()
            v.not_empty = (required or False) and True
            
            try:
                if form:
                    value = v.to_python(value, None)
                else:
                    value = v.from_python(value, None)

            except tg_validators.Invalid, e:
                if form:
                    raise TinyFormError(name.replace('_terp_form/', ''), e.msg, e.value)
            
            kw[name] = value
        
        # Prevent auto conversion from TinyDict
        _eval = TinyDict._eval
        TinyDict._eval = lambda self, v: v
        
        try:
            params, data = TinyDict.split(kw)
            params = params.form or {}
            
            return TinyDict(**params)
        
        finally:
            TinyDict._eval = _eval
    
    def from_python(self):
        return self._convert(False)
    
    def to_python(self):
        return self._convert(True)

if __name__ == "__main__":
    
    kw = {'_terp_view_ids': "[False, 45]",
          'view_ids/_terp_view_ids': '[False, False]',
          'view_ids/child/_terp_view_ids': '[112, 111]'
    }
    
    params, data = TinyDict.split(kw)
    
    params.domain = "[1]"
    params.setdefault('domain', 'something...')
    params.context = "{}"
    params['context'] = "{'id': False}"
    
    print params
    print params.view_ids
    print params.chain_get('view_ids')
    print params.chain_get('view_ids.child')
    print params.chain_get('view_ids.child').view_ids

# vim: ts=4 sts=4 sw=4 si et


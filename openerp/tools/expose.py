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

import os
import re
import types

import cherrypy
import simplejson

from mako.template import Template
from mako.lookup import TemplateLookup

from openerp import rpc
from openerp.tools import utils


__all__ = ['find_resource', 'load_template', 'renderer', 'expose', 'register_template_vars']


def find_resource(package_or_module, *names):

    ref = package_or_module
    if isinstance(package_or_module, basestring):
        ref = __import__(package_or_module, globals(), \
                fromlist=package_or_module.split('.'))

    return os.path.abspath(os.path.join(os.path.dirname(ref.__file__), *names))


def load_template(template, module=None):

    if not isinstance(template, basestring):
        return template

    filters = ["__content"]
    imports = ["from openerp.tools.utils import content as __content"]
    
    if re.match('(.+)\.(html|mako)\s*$', template):

        if module:
            template = find_resource(module, template)
        else:
            template = os.path.abspath(template)
        
        # ask autoreloader to check templates as well
        cherrypy.engine.autoreload.files.add(template)

        dirname = os.path.dirname(template)
        basename = os.path.basename(template)

        lookup = TemplateLookup(directories=[dirname],
                                default_filters=filters,
                                imports=imports)#, module_directory=dirname)

        return lookup.get_template(basename)

    else:
        return Template(template, default_filters=filters, imports=imports)


class _Provider(dict):

    def __getattr__(self, name):
        if name in self:
            return self[name]
        return super(_Provider, self).__getattribute__(name)

    def __setattr__(self, name, value):
        raise AttributeError


_var_providers = {}


def register_template_vars(callback, prefix='oo'):
    providers = _var_providers.setdefault(prefix, [])
    providers.append(callback)


def _cp_vars():

    return {
        'session': cherrypy.session,
        'request': cherrypy.request,
        'config': utils.config,
        'root': cherrypy.request.app.root,
    }


def _py_vars():

    return {
        'url': utils.url,
        'attrs': utils.attrs,
        'attr_if': utils.attr_if,
        'checker': lambda e: utils.attr_if('checked', e),
        'selector': lambda e: utils.attr_if('selected', e),
        'readonly': lambda e: utils.attr_if('readonly', e),
        'disabled': lambda e: utils.attr_if('disabled', e),
    }


def _root_vars():
    return {
        'rpc': rpc,
    }


register_template_vars(_cp_vars, 'cp')
register_template_vars(_py_vars, 'py')
register_template_vars(_root_vars, None)


def renderer(template, module=None):
    
    tmpl = load_template(template, module)
    
    assert isinstance(tmpl, Template), "Invalid template..."

    def wrapper(**kw):

        if not tmpl:
            return

        _vars = {}
        for prefix, cbs in _var_providers.iteritems():
            if prefix:
                provider = _Provider()
                for cb in cbs:
                    provider.update(cb())
                _vars[prefix] = provider
            else:
                for cb in cbs:
                    _vars.update(cb())

        kw = kw.copy()
        kw.update(_vars)

        # XXX mako overrides 'context' template variable...
        if 'context' in kw:
            kw['ctx'] = kw.pop('context')

        return utils.NoEscape(tmpl.render_unicode(**kw))

    return wrapper


def expose(format='html', template=None, content_type=None, allow_json=False):

    def expose_wrapper(func):
        
        template_c = load_template(template, func.__module__)

        def func_wrapper(*args, **kw):

            res = func(*args, **kw)
            
            if format == 'json' or (allow_json and 'allow_json' in cherrypy.request.params):
                cherrypy.response.headers['Content-Type'] = 'text/javascript'
                return simplejson.dumps(res)
            
            cherrypy.response.headers['Content-Type'] = content_type or \
            cherrypy.response.headers.get('Content-Type', 'text/html')

            if isinstance(res, basestring):
                return res
            
            assert isinstance(res, dict), "Exposed method should return string or dict"
            
            _template = load_template(res.get('cp_template'), func.__module__) or template_c
            if _template:
                
                from openerp.widgets import merge_resources
                from openerp.widgets import mochikit
                from openerp.widgets import js_i18n

                res['widget_resources'] = _resources = {}
                _resources = merge_resources(_resources, mochikit.retrieve_resources())
                _resources = merge_resources(_resources, js_i18n.retrieve_resources())
                
                for k, w in res.iteritems():
                    if hasattr(w, 'retrieve_resources') and w.is_root:
                        _resources = merge_resources(_resources, w.retrieve_resources())

                return renderer(_template)(**res).encode("utf-8")

            if not isinstance(res, basestring):
                return unicode(res).encode("utf-8")

            return res

        return utils.decorated(func_wrapper, func, exposed=True)

    return expose_wrapper


# vim: ts=4 sts=4 sw=4 si et


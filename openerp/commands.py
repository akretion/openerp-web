# -*- coding: UTF-8 -*-
"""This module contains functions called from console script entry points."""

import os
import sys
import optparse

from os.path import join, dirname, exists

import cherrypy
from cherrypy._cpconfig import as_dict
from formencode import NestedVariables

from openerp import release
from openerp import rpc

__all__ = ['start']


def nestedvars_tool():
    if hasattr(cherrypy.request, 'params'):
        cherrypy.request.params = NestedVariables.to_python(cherrypy.request.params or {})

cherrypy.tools.nestedvars = cherrypy.Tool("before_handler", nestedvars_tool)
cherrypy.lowercase_api = True


class ConfigurationError(Exception):
    pass


def get_config_file():
    setupdir = dirname(dirname(__file__))
    if exists(join(setupdir, "setup.py")):
        return join(setupdir, "dev.cfg")
    return None


def start():
    """Start the CherryPy application server."""

    parser = optparse.OptionParser(version="%s-%s" % (release.version, release.release))
    parser.add_option("-c", "--config", dest="config", help="specify alternate config file", default=get_config_file())
    (opt, args) = parser.parse_args()

    configfile = opt.config

    if not exists(configfile):
        raise ConfigurationError(_("Could not find configuration file: %s") % configfile)


    cherrypy.config.update({
        'tools.sessions.on':  True,
        'tools.nestedvars.on':  True
    })

    app_config = as_dict(configfile)
    cherrypy.config.update(app_config.pop('global', {}))

    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app_config.update({'/static': {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': static_dir
    }})

    from openerp.controllers import Root
    app = cherrypy.tree.mount(Root(), '/', app_config)

    import pkg_resources
    from openerp.widgets.resource import register_resource_directory

    static = pkg_resources.resource_filename("openerp", "static")
    register_resource_directory(app, "openerp", static)

    # initialize the rpc session
    host = app.config['openerp'].get('host')
    port = app.config['openerp'].get('port')
    protocol = app.config['openerp'].get('protocol')

    #TODO: rpc.session = rpc.RPCSession(host, port, protocol, storage=cherrypy.session)
    rpc.session = rpc.RPCSession(host, port, protocol, storage=dict())

    cherrypy.engine.start()
    cherrypy.engine.block()
    
# vim: ts=4 sts=4 sw=4 si et


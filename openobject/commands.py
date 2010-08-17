import os
import sys
from optparse import OptionParser

import cherrypy
from cherrypy._cpconfig import as_dict

import openobject
import openobject.release

class ConfigurationError(Exception):
    pass

def get_config_file():
    setupdir = os.path.dirname(os.path.dirname(__file__))
    configfile = os.path.join(setupdir, "openerp-web.cfg")
    if os.path.exists(configfile):
        return configfile
    return '/etc/openerp-web.cfg'

def start():

    parser = OptionParser(version="%s" % (openobject.release.version))
    parser.add_option("-c", "--config", metavar="FILE", dest="config",
                      help="configuration file", default=get_config_file())
    parser.add_option("-a", "--address", help="host address, overrides server.socket_host")
    parser.add_option("-p", "--port", help="port number, overrides server.socket_port")
    parser.add_option("--no-static", dest="static",
                      action="store_false", default=True,
                      help="Disables serving static files through CherryPy")
    options, args = parser.parse_args(sys.argv)

    if not os.path.exists(options.config):
        raise ConfigurationError(_("Could not find configuration file: %s") %
                                 options.config)
                                 
    app_config = as_dict(options.config)
    
    openobject.configure(app_config)
    if options.static:
        openobject.enable_static_paths()
    
    if options.address:
        cherrypy.config['server.socket_host'] = options.address
    if options.port:
        try:
            cherrypy.config['server.socket_port'] = int(options.port)
        except:
            pass
    
    cherrypy.engine.start()
    cherrypy.engine.block()
    

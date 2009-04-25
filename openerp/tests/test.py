import os
import sys

from openerp import commands, rpc, tools, tinyres

from cherrypy.test import test, helper
test.prefer_parent_path()

import cherrypy


class TestCase(helper.CPWebCase):
    pass


def setup_server():
    configfile = commands.get_config_file()
    commands.setup_server(configfile)
    cherrypy.config.update({'environment': 'test_suite'})


def secured(fn):
    def wrapper(*args, **kw):
        if not rpc.session.is_logged():
            rpc.session.login("t1", "admin", "admin")
        return fn(*args, **kw)
    return tools.decorated(wrapper, fn, secured=True)

tinyres.secured = secured


def run():
    
    testList = [
        'test_root_controller',
    ]
    
    clp = test.CommandLineParser(testList)
    success = clp.run()
    if clp.interactive:
        print
        raw_input('hit enter')
    sys.exit(success)


if __name__ == '__main__':
    run()

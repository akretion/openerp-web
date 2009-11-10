import os

from itertools import imap
from itertools import izip
from itertools import chain

import cherrypy

from _base import Widget
from _utils import OrderedSet
from _utils import Enum

from openerp import tools

locations = Enum(["head", "bodytop", "bodybottom"])


class Resource(Widget):

    location = locations.head

    @property
    def name(self):
        return None


class Link(Resource):

    params = {
        'link': None,
    }

    _filename = None
    modname = None

    def __init__(self, modname, filename, location=locations.head, **kw):
        super(Link, self).__init__(modname=modname, location=location, **kw)
        self._filename = filename
        
    def get_link(self):
        return cherrypy.request.app.script_name + "/cp_widgets/%s/%s" % (self.modname, self.filename)
    
    def get_file(self):
        return self._filename
    
    link = property(lambda self: self.get_link())
    filename = property(lambda self: self.get_file())

    def __eq__(self, other):
        return getattr(other, 'link', None) == self.link

    def __hash__(self):
        return hash(self.link)


class JSLink(Link):

    template = """\
    <script type="text/javascript" src="${link}" ${py.attrs(charset=charset, defer=defer)}></script>\
    """

    params = {
        'charset': 'The character encoding of the linked script',
        'defer': 'If true, browser may defer execution of the script'
    }

    charset = None
    defer = None


class CSSLink(Link):

    params = {
        'media': 'Specify the media attribute for the css link tag'
    }

    template = """\
    <link rel="stylesheet" type="text/css" href="${link}" ${py.attrs(media=media)}/>\
    """


class Source(Resource):

    params = {
        'src': 'The source text',
    }

    def __init__(self, src, location=locations.head, **kw):
        super(Source, self).__init__(src=src, location=location, **kw)

    def __hash__(self):
        return hash(self.src)

    def __eq__(self, other):
        return self.src == getattr(other, 'src', None)


class JSSource(Source):
    """A JavaScript source snippet."""

    template = """\
    <script type="text/javascript" ${py.attrs(defer=defer)}>
        ${src|n}
    </script>\
    """

    params = {
        'defer': 'If true, browser may defer execution of the script'
    }


class CSSSource(Source):
    """A CSS source snippet."""

    template = """\
    <style type="text/css" ${py.attrs(media=media)}>
        ${src|n}
    </style>\
    """

    params = {
        'src': 'The CSS source for the link',
        'media' : 'Specify the media the css source link is for'
    }

    media = "all"

def register_resource_directory(config, modulename, directory):
    """Set up an application wide static resource directory...
    """

    #assert isinstance(app, cherrypy.Application), "Excepected cherrypy.Application"

    directory = os.path.abspath(directory)
    config.update({'/cp_widgets/%s' % modulename: {
        'tools.staticdir.on': True,
        'tools.staticdir.dir': directory
    }})


class _StaticProvider(object):
    
    def js(self, module, resource, location=locations.head):
        
        if not resource.startswith("javascript/"):
            resource = "javascript/" + resource
            
        return JSLink(module, resource, location).display()
    
    def css(self, module, resource, location=locations.head):
        
        if not resource.startswith("css/"):
            resource = "css/" + resource
            
        return CSSLink(module, resource, location).display()
    
    def __call__(self, module, resource):
        return '/cp_widgets/%s/%s' % (module, resource)
    
    
def _cp_vars():
    
    return {
        'static': _StaticProvider()
    }

tools.register_template_vars(_cp_vars, 'cp')


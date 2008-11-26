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

import re
import random
import locale

from base64 import b64encode, b64decode
from StringIO import StringIO

import turbogears as tg
import wikimarkup

from form import Text

_image = re.compile(r'img:(.*)\.(.*)', re.UNICODE)
_internalLinks = re.compile(r'\[\[.*\]\]', re.UNICODE)

class WikiParser(wikimarkup.Parser):
    
    def parse(self, text):
        text = wikimarkup.to_unicode(text)
        text = self.strip(text)
        text = self.addImage(text)
        text = super(WikiParser, self).parse(text)
        return text
    
    def addImage(self, text):
        def image(path):
            file = path.group().replace('img:','')
            if file.startswith('http') or file.startswith('ftp') or file.startswith('http'):
                return "<img src='%s'/>" % (file)
            else:
                return "<img src='/wiki/getImage?file=%s'/>" % (file)
            
        bits = _image.sub(image, text) 
        return bits
    
    def addInternalLinks(self, text):
        from openerp import rpc
        proxy = rpc.RPCProxy('wiki.wiki')
        def link(path):
            link = path.group().replace('[','').replace('[','').replace(']','').replace(']','').split("|")
            
            mids = proxy.search([('name','ilike',link[0])])
            if not mids:
                mids = [1]
            link_str = ""
            if len(link) == 2:
                link_str = "<a href='/form/view?model=wiki.wiki&amp;id=%s'>%s</a>" % (mids[0], link[1])
            elif len(link) == 1:
                link_str = "<a href='/form/view?model=wiki.wiki&amp;id=%s'>%s</a>" % (mids[0], link[0])
            
            return link_str
        
        bits = _internalLinks.sub(link, text) 
        return bits

def wiki2html(text, showToc=True):
    p = WikiParser(show_toc=showToc)
    return p.parse(text)

class WikiWidget(Text):
    template = "openerp.widgets.templates.wiki"
    
    params = ["data"]
    css = [tg.widgets.CSSLink('openerp', 'css/wiki.css')]
    javascript = [tg.widgets.JSLink("openerp", "javascript/textarea.js")]

    data = None
    
    def __init__(self, attrs):
        super(WikiWidget, self).__init__(attrs)
        self.data = None

    def set_value(self, value):
        super(WikiWidget, self).set_value(value)
        
        if value:
            text = value+'\n\n'
            html = wiki2html(text, True)
            self.data = html

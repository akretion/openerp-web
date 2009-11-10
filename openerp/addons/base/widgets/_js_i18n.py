from openerp import i18n
from openerp import tools

from _base import Widget
from _resource import JSLink


def _get_locale():
    lang = i18n.get_locale()
    if len(lang) == 2:
        lang = lang + '_' + lang
    if len(lang) > 2:
        country = lang[3:].upper()
        lang = lang[:2] + "_" + country
    return lang

class JSCatelog(JSLink):
    
    def get_file(self):
        
        fname = super(JSCatelog, self).get_file()
        lang = _get_locale()
        
        if i18n.is_locale_supported(lang):
            fname = "javascript/i18n/%s.js" % (lang)
            
        return fname

class JSI18n(Widget):
    javascript = [JSLink("base", 'javascript/i18n/i18n.js'),
                  JSCatelog('base', 'javascript/i18n/en_US.js'),]

js_i18n = JSI18n()


# Auto generate language files from gettext catalogs.

import os
import simplejson

def __generate_catalog(locale):

    if not i18n.is_locale_supported(locale):
        return

    fname = tools.find_resource("base",  "static/javascript/i18n/%s.js" % locale)
    cname = os.path.join(i18n.get_locale_dir(), locale, 'LC_MESSAGES', 'messages.mo')

    if os.path.exists(fname) and os.path.getmtime(fname) >= os.path.getmtime(cname):
        return

    print "Generating JavaScript i18n message catalog for %s..." % locale
    messages = {}
    try:
        messages = i18n.get_catalog(locale=locale)._catalog
        messages.pop("")
    except Exception, e:
        pass
    messages = simplejson.dumps(messages)

    catalog = """
// Auto generated file. Please don't modify.
var MESSAGES = %(messages)s;

""" % dict(messages=messages)

    try:
        fo = open(fname, 'w')
        fo.write(catalog)
        fo.close()
    except Exception, e:
        pass

def __generate_catalogs():
    for lang in os.listdir(i18n.get_locale_dir()):
        __generate_catalog(lang)

__generate_catalogs()

# vim: ts=4 sts=4 sw=4 si et


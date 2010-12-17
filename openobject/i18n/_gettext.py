import os

import cherrypy

import babel
import babel.support

from openobject.i18n.utils import get_locale


__all__ = ['get_translations', 'load_translations', 'gettext', 'install']


_translations = {}


def get_translations(locale, domain=None):
    domain = domain or "messages"

    domain_catalog = _translations.setdefault(domain, {})

    if locale in domain_catalog:
        return domain_catalog[locale]
    return domain_catalog[locale.language]

def _load_messages_translations(domain, locales, path):
    catalog = _translations.setdefault(domain, {})
    for lang in locales:
        tr = babel.support.Translations.load(path, [lang], domain)
        if isinstance(tr, babel.support.Translations):
            if lang in catalog:
                catalog[lang].merge(tr)
            else:
                catalog[lang] = tr

def _load_javascript_translations(domain, locales, path):
    catalog = _translations.setdefault(domain, {})
    jspath = os.path.join(os.path.dirname(path), "static", "javascript", "i18n")
    for lang in locales:
        fname = os.path.join(jspath, "%s.js" % lang)
        if os.path.exists(fname):
            _all = catalog.setdefault(lang, [])
            _all.append(fname)

_translations_loaders = {
    'messages': _load_messages_translations,
    'javascript': _load_javascript_translations
}
def load_translations(path, locales=None, domain=None):
    domain = domain or "messages"

    if not locales:
        locales = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
    _translations_loaders[domain](domain, locales, path)

def _gettext(key, locale=None, domain=None):
    """Get the gettext value for key.

    Added to builtins as '_'. Returns Unicode string.

    @param key: text to be translated
    @param locale: locale code to be used.
        If locale is None, gets the value provided by get_locale.

    """
    if locale is None:
        locale = get_locale()
    elif not isinstance(locale, babel.Locale):
        locale = babel.Locale.parse(locale)
    if key == '':
        return '' # special case
    try:
        return get_translations(locale, domain).ugettext(key)
    except KeyError:
        return key

class lazystring(object):
    """Has a number of lazily evaluated functions replicating a string.

    Just override the eval() method to produce the actual value.

    """

    def __init__(self, func, *args, **kw):
        self.func = func
        self.args = args
        self.kw = kw

    def eval(self):
        return self.func(*self.args, **self.kw)

    def __unicode__(self):
        return unicode(self.eval())

    def __str__(self):
        return str(self.eval())

    def __mod__(self, other):
        return self.eval() % other

    def __cmp__(self, other):
        return cmp(self.eval(), other)

    def __eq__(self, other):
        return self.eval() == other

    def __deepcopy__(self, memo):
        return self

def lazify(func):
    def newfunc(*args, **kw):
        lazystr = lazystring(func, *args, **kw)
        return lazystr
    return newfunc

_lazy_gettext = lazify(_gettext)

def gettext(key, locale=None, domain=None):
    if cherrypy.request.app:
        return _gettext(key, locale, domain)
    return _lazy_gettext(key, locale, domain)

def gettext2(key, locale=None, domain=None, **kw):
    value = gettext(key, locale, domain)
    if kw:
        try:
            return value % kw or None
        except:
            pass
    return value

def install():
    __builtins__['_'] = gettext2

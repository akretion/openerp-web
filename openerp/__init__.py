import os
import sys

libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'lib')
if os.path.exists(libdir) and libdir not in sys.path:
    sys.path.insert(0, libdir)

del os
del sys
del libdir


def ustr(value):
    """This method is similar to the builtin `str` method, except
    it will return Unicode string.

    @param value: the value to convert

    @rtype: unicode
    @return: unicode string
    """

    if isinstance(value, unicode):
        return value

    if hasattr(value, '__unicode__'):
        return unicode(value)

    if not isinstance(value, str):
        value = str(value)

    try: # first try utf-8
        return unicode(value, 'utf-8')
    except:
        pass

    try: # then extened iso-8858
        return unicode(value, 'iso-8859-15')
    except:
        pass

    # else use default system locale
    from locale import getlocale
    return unicode(value, getlocale()[1])

from i18n import gettext

__builtins__['_'] = gettext
__builtins__['ustr'] = ustr


# vim: ts=4 sts=4 sw=4 si et


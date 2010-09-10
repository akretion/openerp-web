import os

from openobject import i18n
from openobject import tools

from _base import Widget
from _resource import JSLink


class JSI18n(JSLink):

    template = """\
    % for m, tr in translations:
        <script type="text/javascript" src="/${m}/static/javascript/${tr}"></script>
    % endfor
    """

    params = ["translations"]
    def update_params(self, d):

        super(JSLink, self).update_params(d)

        locale = i18n.get_locale()
        trans = i18n.get_translations(locale, domain="javascript") or []

        translations = []

        static_dir = "%sstatic%s" % (os.path.sep, os.path.sep)
        for tr in trans:
            pr, tr = tr.split(static_dir)
            pr = pr.split(os.path.sep)[-1]
            translations.append((pr, tr))

        d.translations = translations


js_i18n = JSI18n(None, None)

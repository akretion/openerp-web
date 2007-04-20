###############################################################################
#
# Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsability of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# garantees and support are strongly adviced to contract a Free Software
# Service Company
#
# This program is Free Software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
###############################################################################

import turbogears as tg
import cherrypy

from screen import Screen

class ViewForm(tg.widgets.Form):
    template = """
    <form xmlns:py="http://purl.org/kid/ns#" method="post" id="${name}" name="${name}" action="${action}">
        <span py:for="field in hidden_fields" py:replace="field.display(value_for(field), **params_for(field))"/>
        <span py:if="screen" py:replace="screen.display(value_for(screen), **params_for(screen))"/>
    </form>
    """

    member_widgets = ['screen']
    javascript = [tg.widgets.JSLink("tinyerp", "javascript/form.js", location=tg.widgets.js_location.bodytop)]

    def __init__(self, params, **kw):

        super(ViewForm, self).__init__(**kw)

        # save reference of params dictionary in requeste
        cherrypy.request.terp_params = params

        cherrypy.request.terp_fields = []

        self.screen = Screen(prefix='', editable=True)

        self.fields = cherrypy.request.terp_fields

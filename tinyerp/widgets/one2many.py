###############################################################################
#
# Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
#
# $Id: list.py 7 2007-03-23 12:58:38Z ame $
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

from interface import TinyWidget
from interface import TinyField

from screen import Screen

class O2M(tg.widgets.CompoundWidget, TinyWidget):
    """One2Many widget
    """
    template = "tinyerp.widgets.templates.one2many"
    params = ['string', 'id']

    member_widgets = ['screen']
    form = None

    def __init__(self, attrs={}):
        TinyWidget.__init__(self, attrs)
        tg.widgets.CompoundWidget.__init__(self, name=self.name)

        #self.colspan = 4
        #self.nolabel = True

        self.model = attrs['relation']

        view = attrs.get('views', {})
        mode = attrs.get('mode', 'tree,form').split(',')

        ids = attrs['value'] or []

        self.screen = Screen(prefix=self.name, model=self.model, ids=ids, view_mode=mode, views_preloaded=view, domain=[], context={})

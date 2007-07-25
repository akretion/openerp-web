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

from turbogears import expose
from turbogears import widgets
from turbogears import controllers
from turbogears import validators
from turbogears import validate

import cherrypy

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from tinyerp import widgets as tw
from tinyerp.tinyres import TinyResource

from tinyerp.utils import TinyDict
from tinyerp.utils import TinyParent

from form import Form

class OpenM2O(Form):
    
    path = '/openm2o'    # mapping from root
    
    @expose(template="tinyerp.subcontrollers.templates.openm2o")
    def create(self, params, tg_errors=None):     
        
        params.editable = True
        form = self.create_form(params, tg_errors)        
        
        form.hidden_fields = [widgets.HiddenField(name='_terp_m2o', default=params.m2o)]        
        
        return dict(form=form, params=params, show_header_footer=False)

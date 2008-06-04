###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt. Ltd. (http://openerp.com) All Rights Reserved.
#
# $Id$
#
# WARNING: This program as such is intended to be used by professional
# programmers who take the whole responsibility of assessing all potential
# consequences resulting from its eventual inadequacies and bugs
# End users who are looking for a ready-to-use solution with commercial
# guarantees and support are strongly advised to contract a Free Software
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
# along with this program; if not, write to the 
# Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
# Boston, MA  02111-1307, USA.
#
###############################################################################

import os
import time
import math
import pkg_resources

from StringIO import StringIO

from turbogears import expose
from turbogears import controllers

import cherrypy

from tinyerp import rpc
from tinyerp import tools
from tinyerp import common

from tinyerp.tinyres import TinyResource
from tinyerp.utils import TinyDict
from tinyerp.widgets.graph import GraphData

class Graph(controllers.Controller, TinyResource):

    @expose('json')
    def pie(self, **kw):
                                
        params, data = TinyDict.split(kw)
        data = GraphData(params.model, params.view_id, params.ids, params.domain, params.context)
        
        return dict(data=data.get_pie_data())
        
    @expose('json')
    def bar(self, **kw):
        
        params, data = TinyDict.split(kw)
        data = GraphData(params.model, params.view_id, params.ids, params.domain, params.context)
        
        return dict(data=data.get_bar_data())

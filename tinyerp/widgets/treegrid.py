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
from turbojson import jsonify

from turbogears import widgets
from interface import TinyField

class TreeGrid(TinyField):
    template="""
    <span xmlns:py="http://purl.org/kid/ns#">
        <span  id="${id}"/>
        <script type="text/javascript">
            var ${id} = new TreeGrid('${id}', '${headers}');

            ${id}.onopen = ${onopen or 'null'};
            ${id}.onselection = ${onselection or 'null'};

            ${id}.action_url = '${action_url or 'null'}';
            ${id}.action_params = ${ustr(action_params or 'null')};

            ${id}.load('${url}', -1, {model: '${model}', fields:'${fields}', domain: "${str(domain)}", field_parent: '${field_parent}'});
        </script>
    </span>
    """

    params = ['id', 'url', 'model', 'headers', 'fields', 'field_parent', 'onopen', 'onselection', 'domain', 'action_url', 'action_params']

    selectable = False
    show_headers = True

    onopen = None
    onselection = None

    action_url = None
    action_params = []

    css = [widgets.CSSLink("tinyerp", "css/treegrid.css")]
    javascript = [widgets.mochikit, widgets.JSLink("tinyerp", "javascript/treegrid.js")]

    def __init__(self, name, model, headers, url, field_parent=None, domain=[]):

        attrs = dict(name=name, model=model, url=url)

        super(TreeGrid, self).__init__(attrs)

        self.id = name
        self.model = model
        self.url = url

        self.domain = domain

        self.headers = jsonify.encode(headers)

        fields = []
        for f, v in headers:
            fields.append(f)

        self.fields = jsonify.encode(fields)
        self.field_parent = field_parent

///////////////////////////////////////////////////////////////////////////////
//
// Copyright (c) 2007 TinyERP Pvt Ltd. (http://tinyerp.com) All Rights Reserved.
//
// $Id$
//
// WARNING: This program as such is intended to be used by professional
// programmers who take the whole responsability of assessing all potential
// consequences resulting from its eventual inadequacies and bugs
// End users who are looking for a ready-to-use solution with commercial
// garantees and support are strongly adviced to contract a Free Software
// Service Company
//
// This program is Free Software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the Free Software
// Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
//
///////////////////////////////////////////////////////////////////////////////

var inlineEdit = function(id, src){

    form = $('view_form');

    act = '/form/edit';

    if (src) {
        n = src.replace('.', '/') + '/_terp_id';
        terp_id = document.getElementsByName(n)[0];
        terp_id.value = id;

        act = getURL(act, {_terp_source: src, _terp_inline: 1});

    } else {
        form._terp_id.value = id;
    }

    form.action = act;
    form.submit();
}
var inlineDelete = function(id, src){

    if (!confirm('Do you realy want to delete this record?')) {
        return false;
    }

    form = $('view_form');

    act = '/form/delete';

    if (src) {
        n = src.replace('.', '/') + '/_terp_id';
        terp_id = document.getElementsByName(n)[0];
        terp_id.value = id;

        act = getURL(act, {_terp_source: src});

    } else {
        form._terp_id.value = id;
    }

    form.action = act;
    form.submit();
}

var submit_form = function(action, src, data){

    if (action == 'delete' &&  !confirm('Do you realy want to delete this record?')) {
        return false;
    }

    form = $("view_form");
    source = src ? (typeof(src) == "string" ? src : src.name) : null;

    form.action = getURL('/form/' + action, {_terp_source: source, _terp_data: data ? data : null});
    form.submit();
}
var submit_value = function(action, src, data){

    form = $("view_form");
    source = src ? (typeof(src) == "string" ? src : src.name) : null;

    form.action = '/openm2o/save';
    form.submit();
}

var buttonClicked = function(name, btype, model, id, sure){

    if (sure && !confirm(sure)){
        return;
    }

    params = {};

    params['_terp_button/name'] = name;
    params['_terp_button/btype'] = btype;
    params['_terp_button/model'] = model;
    params['_terp_button/id'] = id;

    form = $("view_form");
    form.action = getURL('/form/save', params);
    form.submit();
}

/**
 * This function will be used by widgets that has `onchange` trigger is defined.
 *
 * @param name: name/instance of the widget
 */
var onChange = function(name) {

    var caller = $(name);
    var callback = getNodeAttribute(caller, 'callback');

    var prefix = caller.name.split("/");
    prefix.pop();
    prefix = prefix.join("/");
    prefix = prefix ? prefix + '/' : '';

    var model = document.getElementsByName(prefix + '_terp_model')[0].value;

    form = $("view_form");

    vals = {};
    forEach(form.elements, function(e){
        if (e.name && e.name.indexOf('_terp_') == -1 && e.type != 'button'){
            vals['_terp_parent_form/' + e.name] = e.value;
            if (e.attributes['kind']){
                vals['_terp_parent_types/' + e.name] = getNodeAttribute(e, 'kind');
            }
        }
    });

    if (!callback)
        return;

    vals['_terp_caller'] = caller.id;
    vals['_terp_callback'] = callback;
    vals['_terp_model'] = model;

    req = doSimpleXMLHttpRequest(getURL('/form/on_change', vals));

    req.addCallback(function(xmlHttp){
        res = evalJSONRequest(xmlHttp);
        values = res['value'];
		for(var k in values){
			flag = false;
            fld = $(prefix + k);
            if (fld) {
                value = values[k];
                value = value === false || value === null ? '' : value

				if ($(prefix + k + '_id')){
                	fld = $(prefix + k + '_id');
                	flag = true;
                }

                if ((fld.value != value) || flag) {
                	fld.value = value;
                    if (typeof fld.onchange != 'undefined'){
                        fld.onchange();
            	     }
               	}
            }
        }
    });
}

/**
 * This function will be used by many2one field to get display name.
 *
 * @param name: name/instance of the widget
 * @param relation: the TinyERP model
 *
 * @return string
 */
function getName(name, relation){

    var value_field = $(name);
    var text_field = $(value_field.name + '_text');

    if (value_field.value == ''){
        text_field.value = ''
    }

    if (value_field.value){
        var req = doSimpleXMLHttpRequest(getURL('/many2one/get_name', {model: relation, id : value_field.value}));

        req.addCallback(function(xmlHttp){
            var res = evalJSONRequest(xmlHttp);
            text_field.value = res['name'];
        });
    }
}

function openm2o(action, relation, id)
{
    wname = 'select_' + relation;
	id1 = '';
    if (window.opener){
        if (typeof window.popup_counter == "undefined")
            window.popup_counter = 0;

        window.popup_counter += 1;
        wname += window.popup_counter;
    }
	if (action=="new")
		id1 = null;
	else if($(id))
		id1 = $(id) ? $(id).value : null;
	act = getURL('/openm2o/edit', {_terp_model: relation, _terp_view_mode: '[form,tree]', _terp_m2o: id, _terp_id: id1});
	wopen(act, wname, 800, 600);
}


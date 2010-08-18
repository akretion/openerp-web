////////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
//
// $Id$
//
// Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
//
// The OpenERP web client is distributed under the "OpenERP Public License".
// It's based on Mozilla Public License Version (MPL) 1.1 with following 
// restrictions:
//
// -   All names, links and logos of Tiny, Open ERP and Axelor must be 
//     kept as in original distribution without any changes in all software 
//     screens, especially in start-up page and the software header, even if 
//     the application source code has been changed or updated or code has been 
//     added.
//
// -   All distributions of the software must keep source code with OEPL.
// 
// -   All integrations to any other software must keep source code with OEPL.
//
// If you need commercial licence to remove this kind of restriction please
// contact us.
//
// You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
//
////////////////////////////////////////////////////////////////////////////////

function add_filter_row(elem) {
    
    var filter_table = jQuery('#filter_table');
    var filter_opt_tbl = jQuery('#filter_option_table')
    var $cls_tbody = jQuery(elem).closest("tbody")

    if (jQuery(filter_opt_tbl).find('tbody:visible').length == 1 && jQuery($cls_tbody).siblings().length == 1) {
	    if(filter_table.is(':hidden')) {
	        if (jQuery('label#filterlabel').text() == ''){
	            jQuery('label#filterlabel').text(jQuery('select.filter_fields_and option:selected').text())
	            jQuery('label#filterlabel').attr('value', jQuery(elem).val())
	        }
	        filter_table.show();
	    }
    } else {
        var position_tr = jQuery($cls_tbody).find('tr:last').prev();

        if (jQuery($cls_tbody).prev().attr('id') == 'filter_table') {
            var position_tr = filter_table.find('tr:last');
        }
        
        var old_tr = jQuery(filter_opt_tbl).find('tbody:first').find('tr.filter_row_class:first')            
        old_tr.find('input.qstring').css('background', '#FFF');        

        var new_tr = old_tr.clone();
        new_tr.find('label#filterlabel').text(jQuery('select.filter_fields_and option:selected').text());
        new_tr.find('label#filterlabel').attr('value', jQuery(elem).val());
        new_tr.find('input.qstring').css('background', '#fff').val('');
        if (new_tr.is(':hidden')) {
            new_tr.show()
        }
        
        var index_row;
        var $curr_body = position_tr.closest('tbody')
        $curr_body.find('label.filterlabel').each(function(i, v) {
	        var theValue = jQuery(v).text();
	        if (theValue == jQuery('select.filter_fields_and option:selected').text()){                          
	            index_row = i
	            new_tr.find('select.expr').hide()
	            new_tr.find('label#filterlabel').hide()	           
	            new_tr.find('label.and_or').remove()
	            
	            var select_andor = jQuery('<label>', {'class': 'and_or'}).text('OR');               
	            select_andor.insertBefore(new_tr.find('input.qstring'));              
	        }
        });

        if(index_row >= 0) {
             position_tr = $curr_body.find('tr.filter_row_class')[index_row];                        
        }

        jQuery(position_tr).after(new_tr);
    }
    
    if (!jQuery('select.filter_fields_or').closest("tbody").siblings().length) {
        jQuery('select#filter_fields_or').attr('disabled', true);
    }else{
        jQuery('select#filter_fields_or').attr('disabled', false);
    }
}

function addOrBlock(elem){
    
    var filter_option_table = jQuery('#filter_option_table');
    var old_tr = jQuery('#filter_table').next('tbody.actions').find('tr.actions');    
    var tbody = filter_option_table.find('tbody:last');
   
    var action_tr = old_tr.clone();
    action_tr.find('select.filter_fields_or').parent().show();
    action_tr.find('select.filter_fields_or').attr('disabled', false);        
    if (action_tr.is(':hidden')) {
        action_tr.show();
    }
    
    var position_tr = filter_option_table.find('tr:last');
    position_tr.find('select.filter_fields_or').parent().hide();    
    
    var newtbody = jQuery('<tbody>');    
    var tr = jQuery('<tr id="or">');
    var td = jQuery('<td>', {'colspan': '4'});
    td.append(jQuery('<div class="filter-lsep">').append(jQuery('<hr class="filter-hr"/>')));
    td.append(jQuery('<div class="filter-msep">Or</div>'));
    td.append(jQuery('<div class="filter-rsep">').append(jQuery('<hr class="filter-hr"/>')));    
    jQuery(tr).append(td)
    jQuery(newtbody).append(tr)
    
    var oldTr = filter_option_table.find('tr:first');
    var new_tr = oldTr.clone();
    new_tr.find('label#filterlabel').text(jQuery('select.filter_fields_or option:selected').text());
    new_tr.find('label#filterlabel').attr('value', jQuery(elem).val());    
    new_tr.find('input.qstring').css('background', '#FFF').val('');
    
    jQuery(tr).after(new_tr);
    jQuery(new_tr).after(action_tr);        
    jQuery(tbody).after(newtbody);   
}

function switch_searchView(d) {
    
    var domain = eval(d)
    var operators = [];
    var tbodys = [];
    var trs = 0;
    var tbody = jQuery("<tbody/>");
    var prev_row_field = '';
    var old_tr = jQuery('#filter_option_table tbody:first').find('tr.filter_row_class:first');
    var action_tbody = jQuery('#filter_option_table').find('tbody.actions');
    var selection_options =  jQuery('tbody.actions tr.actions').find('select.filter_fields_and:first');
    
    jQuery('#filter_table').hide()   

    for (i=0; i<domain.length; i++) {

        var item = domain[i];
        if (item.length==1) {
            operators.push(item);            
        }      
        else {
	        var new_tr = old_tr.clone();
	        var txt =  jQuery(selection_options).find('option[value='+ item[0] + ']').text()
	        new_tr.find('label#filterlabel').text(txt);
	        new_tr.find('label#filterlabel').attr('value', item[0]);
	        new_tr.find('select.expr').val(item[1]);
	        old_tr.find('input.qstring').css('background', '#FFF').val('');
	        new_tr.find('input.qstring').attr('value', item[2]);

	        if (trs==0 || operators[operators.length-1]=='&') {
                tbody.append(new_tr)
                if (trs>0)
                   operators.splice(operators.length-1, 1);
            }
            else if(prev_row_field!=item[0] && operators[operators.length-1]=='|') {
                tbodys.push(tbody);
                tbody = jQuery("<tbody/>");
                tbody.append(new_tr);
                trs = 1;
                operators.splice(operators.length-1, 1);
            }            
            else if(prev_row_field==item[0] && operators[operators.length-1]=='|') {
                new_tr.find('label#filterlabel').hide();
                new_tr.find('select.expr').hide();
                var select_andor = jQuery('<label>', {'class': 'and_or'}).text('OR');               
                select_andor.insertBefore(new_tr.find('input.qstring'));
                tbody.append(new_tr);
                operators.splice(operators.length-1, 1);
            }      
            trs ++;            
            prev_row_field = item[0];
        }                
    }

    if (domain.length){
        tbodys.push(tbody)
        jQuery('#filters').toggleClass('group-expand group-collapse');
        jQuery('#filter_option_table').toggle();
        if (action_tbody.is(':visible')){ 
            action_tbody.hide()
        }
    }

    for (i=0; i<tbodys.length; i++) {	       

        if (tbodys[i + 1]) {
            var trOr = jQuery('<tr id="or">');
		    var td = jQuery('<td>', {'colspan': '4'});
		    td.append(jQuery('<div class="filter-lsep">').append(jQuery('<hr class="filter-hr"/>')));
		    td.append(jQuery('<div class="filter-msep">Or</div>'));
		    td.append(jQuery('<div class="filter-rsep">').append(jQuery('<hr class="filter-hr"/>')));    
		    jQuery(trOr).append(td)
		    tbodys[i + 1].prepend(trOr)		         
        }
        if (tbodys[i - 1]) {
            tbodys[i - 1].find('tr.actions td.filter_column').hide()               
        }

        var actTr = action_tbody.find('tr.actions').clone(true);
        actTr.find('select#filter_fields_or').attr('disabled', false);
        jQuery(tbodys[i]).append(actTr)
        $('#filter_option_table').append(tbodys[i])
    }
}

function remove_filter_row(element) {

    var node = jQuery(element).closest('tr');
    var t = jQuery(node).closest('tbody')
    var $paren = t.parent()
    var prev_body = jQuery($paren.children('tbody')[t.index()-1])
    var next_body = jQuery($paren.children('tbody')[t.index()+1])   

    if (t.find('tr.filter_row_class').length <= 1 && t.attr('id')!='filter_table') {
                
        if (!(next_body.length >= 1) || !(prev_body.length >= 1)) {        
            jQuery(prev_body.find('td.filter_column')).show();
        }

        jQuery(node).closest('tbody').remove();
        
        if (jQuery('#filter_option_table tbody:visible').length == 2 ) {            
            var body_next = jQuery('#filter_option_table').find('tbody:first')
            jQuery(body_next).find('#or').remove()
        }        
    }
    
    if(node.is(':only-child')) {

        if (jQuery('#filter_option_table tbody:visible').length >= 1 && node.closest("tbody").siblings().length > 1){            
            jQuery('#filter_table').next().hide()
            jQuery('#filter_option_table').find('tr#or:first').hide()
        }

        node.find('input.qstring').css('background', '#FFF').val('');
        jQuery('label#filterlabel').text('')
        jQuery('label#filterlabel').attr('value', '')
        jQuery('select#filter_fields_or').attr('disabled', true)
        jQuery('#filter_table').hide();        
	    
    } else {

        if(node.is(':last-child')) {
            node.prev().find('.and_or').remove();
        }

        if(node.next().find('label.and_or').is(':visible')){             
             node.next().remove();
        }
        else{
			if (jQuery('#filter_option_table tbody:visible').length == 0) {
			    jQuery('tbody.actions').show()
			    jQuery('tbody.actions').find('tr.actions').find('td.filter_column').show()                
			}
			
			if (jQuery('#filter_option_table tbody:visible').length == 1){   
	           jQuery('#filter_option_table').find('tr#or:first').hide()
	        }
	        node.remove();            
        }
    }
}

/**
 * Checks if a type is considered order-able, so that we can setup the right search operators for the operand
 * @param type the field's type to consider for operator replacement
 */
function isOrderable(type) {
    return jQuery.inArray(type, ['integer', 'float', 'date', 'datetime', 'boolean']) != -1;
}

/**
 * To return the keys of an object. use jQuery.keys(obj).
*/
jQuery.extend({
    keys: function(obj){
        var a = [];
        $.each(obj, function(k){ a.push(k) });
        return a;
    }
})

function display_Customfilters(all_domains, group_by_ctx) {    
    var Allrecords = {};
    var parent_tbody = jQuery('#filter_option_table > tbody')

    parent_tbody.each(function () {
	    var children = jQuery(this).find('> .filter_row_class');	    
	    var record = {};
	    var pid = jQuery(this).index()

	    children.each(function () {
	        var $constraint_value = jQuery(this).find('input.qstring');
	        var $fieldname = jQuery(this).find('label.filterlabel');
	        var id = jQuery(this).parent().find('> .filter_row_class').index(this);

	        if($constraint_value.val()) {
	            var rec = {};
	            rec[$fieldname.attr('value')] = $constraint_value.val();
	            record[id] = rec;
	        }
	    });

	    if (jQuery.keys(record).length != 0){
	       Allrecords[pid] = record;
	    }
    });
    
    openobject.http.postJSON('/openerp/search/get', {
        record: serializeJSON(Allrecords),
        _terp_model: jQuery('#_terp_model').val()
    }).addCallback(function(obj) {
        var custom_domain = [];
        if(obj.error) {
            var children = jQuery('#filter_option_table tbody').find('> .filter_row_class')
            children.each(function () {
                if(jQuery(this).find('label.filterlabel').attr('value') == obj['error_field']) {
                    jQuery(this).find('input.qstring').css('background', '#f66').val(obj.error);
                }
            });
        }
        var form_result = obj.frm;
        var tbody_keys = jQuery.keys(form_result)

        if(form_result) {
            // By property, we get incorrect ordering
            for(var ind=0; ind<tbody_keys.length ;ind++){
                var All_domain = [];
                var group = []
                var tbody_frm_ind = form_result[tbody_keys[ind]]; //tbody dictionary
                var trs_keys = jQuery.unique(jQuery.keys(tbody_frm_ind)); //sort trs

                for(index = 0; index<trs_keys.length ; index++) {
	                var return_record = tbody_frm_ind[trs_keys[index]];
	                var $curr_body = jQuery('#filter_option_table > tbody').eq(tbody_keys[ind]);              	                
	                var $row = jQuery($curr_body.find('> .filter_row_class').eq(trs_keys[index]));                	                
	                var $next_row = []

	                if (jQuery($row.next('tr.filter_row_class')).find('input.qstring').val() != ''){
	                       $next_row = jQuery($row.next());
	                }

	                var type = return_record.type;	                
	                var temp_domain = [];
	                var grouping = $next_row.length != 0 ? $next_row.find('label.and_or').text(): null;

	                if (group.length==0) {
                        var new_grp = $curr_body.find('tr.filter_row_class:gt('+trs_keys[index]+')')
                        new_grp = new_grp.find('td.filter_column:not(:has(label))').find('input.qstring[value]')                        
                        if (new_grp.length){
                            group.push('&')
                        }
                    }
                    if(grouping) {
                        temp_domain.push(grouping == 'AND' ? '&' : '|');                        
                    }

	                var field = return_record['rec'];
	                var comparison = $row.find('select.expr').val();	                
	                var value = return_record['rec_val'];

	                switch (comparison) {
	                    case 'ilike':
	                    case 'not ilike':
	                        if(isOrderable(type)) {
	                            comparison = (comparison == 'ilike' ? '=' : '!=');
	                        }
	                        break;
	                    case '<':
	                    case '>':
	                        if(!isOrderable(type)) {
	                            comparison = '=';
	                        }
	                        break;
	                    case 'in':
	                    case 'not in':
	                        if(typeof value == 'string') {
	                            value = value.split(',');
	                        } else {
	                            /* very weird array-type construct
	                               looks a bit like [[6, 0, [list of ids here]]]
	                             */
	                            value = value[value.length - 1][value[value.length - 1].length - 1]
	                        }
	                        break;
	                }
	                
	                if ($row.find('label.and_or').length>0 || grouping){                       
                        temp_domain.push(field, comparison, value);
                        group.push(temp_domain);
                    }
                    else{
                        group.push(field, comparison, value)
                    }

                    if (!grouping) {             
                        All_domain.push(group);                        
                        group = [];
                    }     	                
	            }

	            if (All_domain.length) {
	               custom_domain.push(All_domain);
	            }
            };
        }
        final_search_domain(serializeJSON(custom_domain), all_domains, group_by_ctx);
    });
}

var group_by = new Array();
var filter_context = [];

function parse_filters(src, id) {
    var all_domains = {};
    var check_domain = 'None';
    var domains = {};
    var search_context = {};
    var all_boxes = [];
    var domain = 'None';
    
    var check_groups = jQuery('#_terp_group_by_ctx').val();
    if(check_groups!='[]') {
        check_groups = eval(check_groups);
        for(i in check_groups) {
            if(jQuery.inArray(check_groups[i], group_by) < 0) {
                group_by.push(check_groups[i])
            }
        }   
    }
    if(src) {
        var source = jQuery(src);
        if(jQuery(id).hasClass('inactive')) {
            source.closest('td').addClass('grop_box_active');
            jQuery(src).attr('checked', true);
            if(source.attr('group_by_ctx') && source.attr('group_by_ctx') != 'False') {
                group_by.push(source.attr('group_by_ctx'));
            }

            if(source.attr('filter_context') && source.attr('filter_context') != '{}') {
                filter_context.push(source.attr('filter_context'));
            }
        } else {
            source.closest('td').removeClass('grop_box_active');
    		jQuery(src).attr('checked', false);
    		
    		group_by = jQuery.grep(group_by, function(grp) {
                return grp != source.attr('group_by_ctx');
            });
            
            if(source.attr('filter_context') && source.attr('filter_context')!='{}') {
                var filter_index = jQuery.inArray(source.attr('filter_context'), filter_context);
                if(filter_index >= 0) {
                    filter_context.splice(filter_index, 1);
                }
            }
    	}
        jQuery(id).toggleClass('active inactive');
    }
    
    jQuery('#_terp_filters_context').val(filter_context);
    
    var filter_table = getElement('filter_table');
    forEach($$('[name]', 'search_filter_data'), function(d) {
        var value;
        if (d.type != 'checkbox' && d.name && d.value && d.name.indexOf('_terp_') == -1 && d.name != 'filter_list' && d.name != 'flashvars' && d.name != 'wmode') {
            value = d.value;
            if (getNodeAttribute(d, 'kind') == 'selection') {
                value = parseInt(d.value);
                if(getNodeAttribute(d, 'search_context')) {
                    search_context['context'] = getNodeAttribute(d, 'search_context');
                    search_context['value'] = value;
                }
            }
            if (getNodeAttribute(d, 'kind') == 'many2one'){
                value = openobject.dom.get(d.name+'_text').value || value;
                if (getNodeAttribute(d, 'm2o_filter_domain')){
                    value = 'm2o_'+ value
                }
            }
            domains[d.name] = value;
        }
    });
    domains = serializeJSON(domains);
    all_domains['domains'] = domains;
    all_domains['search_context'] =  search_context;
    var selected_boxes = getElementsByTagAndClassName('input', 'grid-domain-selector');
    
    forEach(selected_boxes, function(box){
        if (box.id && box.checked && box.value != '[]') {
            all_boxes = all_boxes.concat(box.value);
        }
    });
    
    var checked_button = all_boxes.toString();
    check_domain = checked_button.length > 0? checked_button.replace(/(]\,\[)/g, ', ') : 'None';
    all_domains['check_domain'] = check_domain;
    
    if (openobject.dom.get('filter_list')) {
        all_domains['selection_domain'] = jQuery('#filter_list').val();
    }
    
    all_domains = serializeJSON(all_domains);
    return all_domains;
}

function search_filter(src, id) {
    var all_domains = parse_filters(src, id);
    var filters = jQuery('#filter_table');    
    
    if(filters.is(':visible') || jQuery('#_terp_filter_domain').val() != '[]') {        
        display_Customfilters(all_domains, group_by);
    } else {
        var custom_domain = jQuery('#_terp_filter_domain').val() || '[]';
        final_search_domain(custom_domain, all_domains, group_by);
    }
}

function save_filter() {
    var domain_list = parse_filters();
    var custom_domain = jQuery('#_terp_filter_domain').val() || '[]';
    var req = openobject.http.postJSON('/openerp/search/eval_domain_filter', {
        'all_domains': domain_list,
        'source': '_terp_list',
        'custom_domain': custom_domain,
        'group_by_ctx': group_by});
    req.addCallback(function(obj) {
        var sf_params = {'model': jQuery('#_terp_model').val(), 'domain': obj.domain, 'group_by': group_by, 'flag': 'sf'};
        openobject.tools.openWindow(openobject.http.getURL('/openerp/search/save_filter', sf_params), {
                width: 500,
                height: 240
            });
    });
    
}

function manage_filters() {
    openLink(openobject.http.getURL('/openerp/search/manage_filter', {
        'model': jQuery('#_terp_model').val()}));
}

function final_search_domain(custom_domain, all_domains, group_by_ctx) {
	var req = openobject.http.postJSON('/openerp/search/eval_domain_filter', 
		{source: '_terp_list',
		model: jQuery('#_terp_model').val(), 
		custom_domain: custom_domain,
		all_domains: all_domains,
		group_by_ctx: group_by_ctx
	});
	req.addCallback(function(obj){
		if (obj.flag) {
			var params = {'domain': obj.sf_dom,
				'model': openobject.dom.get('_terp_model').value,
				'flag': obj.flag};
							
			if(group_by_ctx!=''){
				params['group_by'] = group_by_ctx;
			}				
			openobject.tools.openWindow(openobject.http.getURL('/openerp/search/save_filter', params), {
				width: 400,
				height: 250
			});
		}
		
        if (obj.action) { // For manage Filter
            openLink(openobject.http.getURL('/openerp/search/manage_filter', {
                action: serializeJSON(obj.action)}));
        }
		
		if (obj.domain) { // For direct search
			var in_req = eval_domain_context_request({
				source: '_terp_list', 
				domain: obj.domain, 
				context: obj.context,
				group_by_ctx: group_by_ctx
			});
			
			in_req.addCallback(function(in_obj){
		    	openobject.dom.get('_terp_search_domain').value = in_obj.domain;
		    	openobject.dom.get('_terp_search_data').value = obj.search_data;
		    	openobject.dom.get('_terp_context').value = in_obj.context;
		    	openobject.dom.get('_terp_filter_domain').value = obj.filter_domain;
		    	jQuery('#_terp_group_by_ctx').val(in_obj.group_by)
	    		new ListView('_terp_list').reload();
			});	
		}
	});
}

var ENTER_KEY = 13;
function search_on_return(e) {
    if (e.which == ENTER_KEY){
        // Avoid submitting form when using RETURN on a random form element
        if(!jQuery(e.target).is('button')) {
            e.preventDefault();
        }
    	search_filter();
    }
}
function initialize_search() {
    var filter_table = jQuery('#filter_table');
    var fil_dom = jQuery('#_terp_filter_domain');

    if((filter_table.length && filter_table.is(':hidden')) &&
            (fil_dom.length && fil_dom.val() != '[]')) {
        filter_table.show();
    }
    jQuery('#search_filter_data').keydown(search_on_return);
}
jQuery(document).ready(initialize_search);

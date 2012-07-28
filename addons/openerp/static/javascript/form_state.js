////////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2007-TODAY OpenERP SA. All Rights Reserved.
//
// $Id$
//
// Developed by OpenERP (http://openerp.com) and Axelor (http://axelor.com).
//
// The OpenERP web client is distributed under the "OpenERP Public License".
// It's based on Mozilla Public License Version (MPL) 1.1 with following 
// restrictions:
//
// -   All names, links and logos of OpenERP must be kept as in original
//     distribution without any changes in all software screens, especially
//     in start-up page and the software header, even if the application
//     source code has been changed or updated or code has been added.
//
// You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
//
////////////////////////////////////////////////////////////////////////////////

function form_hookContextMenu(){
    if (!openobject.dom.get('_terp_list')) {
        MochiKit.Signal.connect(window.document, 'oncontextmenu', on_context_menu);
    }
}

function form_hookStateChange() {
    var fields = {};

    jQuery('td.item[states], td.label[states], div.tabbertab[states]').each(function() {
        var $this = jQuery(this);
        var widget = $this.attr('widget');
        var prefix = widget.slice(0, widget.lastIndexOf('/')+1) || '';

        // convert states from Python serialization to JS/JSON
        var states = eval(
                '(' + $this.attr('states')
                      .replace(/u'/g, "'")
                      .replace(/True/g, '1')
                      .replace(/False/g, '0') + ')');

        var state = openobject.dom.get(prefix + 'state') || openobject.dom.get(prefix + 'x_state');
        if (state) {
            fields[state.id] = state;
            var $state = jQuery(state).bind('onStateChange', MochiKit.Base.partial(form_onStateChange, this, widget, states));
            $state.change(function (){
                jQuery(this).trigger('onStateChange');
            });
        }
    });
    
    for(var field in fields) {
        jQuery(field).trigger('onStateChange');
    }
}

function list_hookStateChange(list_name) {
    var fields = {};
    var list_fields_with_states = [ 'table[id='+list_name+'_grid] input.[states]',
				    'table[id='+list_name+'_grid] selection.[states]' ].join(', ');
    jQuery(list_fields_with_states).each(function() {
        var $this = jQuery(this);
        var attrs = $this.attr('attrs') || '{}';
        var widget = $this.attr('widget') || '';
        var container = this;
        var prefix = widget.slice(0, widget.lastIndexOf('/')+1) || '';

        // convert states from Python serialization to JS/JSON
        var states = eval(
                '(' + $this.attr('states')
                      .replace(/u'/g, "'")
                      .replace(/True/g, '1')
                      .replace(/False/g, '0') + ')');

        var state = form_find_field_in_context(prefix, 'state', $this);
        if (!state || !state.length) {
            state = form_find_field_in_context(prefix, 'x_state', $this);
        }

        if (state && state.length) {
            var $state = state.bind('onStateChange', MochiKit.Base.partial(form_onStateChange, container, this, states));
            $state.change(function (){
                jQuery(this).trigger('onStateChange');
            });
            state.trigger('onStateChange');
        }

    });
}

function form_onStateChange(container, widget, states, evt) {
    var src;
    if(evt.src)
        src = evt.src();
    else
        src = evt.target;

    var value = typeof(src.value) == "undefined" ? getNodeAttribute(src, 'value') || src.innerHTML : src.value;
    var $field = jQuery(idSelector(widget));

    if (MochiKit.Base.isArrayLike(states)) {
        form_setVisible(container, widget, findIdentical(states, value) > -1);
        return;
    }

    var has_readonly = false;
    var has_required = false;

    for(var a in states) {
        a = states[a];
        has_readonly = has_readonly || typeof(a.readonly) != "undefined";
        has_required = has_required || typeof(a.required) != "undefined";
    }

    var attr = states[value];
    if (has_readonly) {
        if (attr) {
            form_setReadonly(container, widget, attr['readonly']);
        }
        else {
            form_setReadonly(container, widget, parseInt($field.attr('fld_readonly')));
        }
    }
    if (has_required) {
        if (attr) {
            form_setRequired(container, widget, attr['required']);
        }
        else {
            form_setRequired(container, widget, parseInt($field.attr('fld_required')));
        }
    }
}

function form_hookAttrChange() {
    var $items = jQuery('[attrs]');
    var fields = {};

    $items.each(function(){
        var $this = jQuery(this);
        var attrs = $this.attr('attrs') || '{}';
        var widget = $this.attr('widget') || '';
        var container = this;
        var prefix = widget.slice(0, widget.lastIndexOf('/')+1) || '';

        // Convert Python statement into it's equivalent in JavaScript.
        attrs = attrs.replace(/\(/g, '[');
        attrs = attrs.replace(/\)/g, ']');
        attrs = attrs.replace(/True/g, '1');
        attrs = attrs.replace(/False/g, '0');
        attrs = attrs.replace(/\buid\b/g, window.USER_ID);

        try {
            attrs = eval('(' + attrs + ')');
        } catch(e){
            return;
        }

        for (var attr in attrs) {
            var expr_fields = {}; // check if field appears more then once in the expr

            if (attrs[attr] == ''){
                return form_onAttrChange(container, widget, attr, attrs[attr], $this);
            }

            forEach(attrs[attr], function(n){

                if (typeof(n) == "number") { // {'invisible': [1]}
                    return form_onAttrChange(container, widget, attr, n, $this);
                }

                var name = prefix + n[0];
                var field = openobject.dom.get(name);
                if (field && !expr_fields[field.id]) {
                    fields[field.id] = 1;
                    expr_fields[field.id] = 1;
                    // events disconnected during hook_onStateChange,
                    // don't redisconnect or may break onStateChange
                    var $field = jQuery(field).bind('onAttrChange', partial(form_onAttrChange, container, widget, attr, attrs[attr], $this));
                    $field.change(partial(form_onAttrChange, container, widget, attr, attrs[attr], $this));
                }
            });
        }
    });

    for(var field in fields) {
        jQuery(idSelector(field)).trigger('onAttrChange');
    }
}

function list_hookAttrChange(list_name) {
    jQuery('table[id='+list_name+'_grid] [attrs]').each(function () {
        var $this = jQuery(this);
        var attrs = $this.attr('attrs') || '{}';
        var widget = $this.attr('widget') || '';
        var container = this;
        var prefix = widget.slice(0, widget.lastIndexOf('/')+1) || '';

        // Convert Python statement into it's equivalent in JavaScript.
        attrs = attrs.replace(/\(/g, '[');
        attrs = attrs.replace(/\)/g, ']');
        attrs = attrs.replace(/True/g, '1');
        attrs = attrs.replace(/False/g, '0');
        attrs = attrs.replace(/\buid\b/g, window.USER_ID);

        try {
            attrs = eval('(' + attrs + ')');
        } catch(e){
            return;
        }

        var row_is_editable = $this.parents('tr.grid-row').is('.editors')
        for (var attr in attrs) {
            if (!row_is_editable && attr != 'invisible') {
                // when row is not in editable mode we only care about invisible attributes
                // as others attrs (readonly, required) won't have any effects.
                continue;
            }
            if (attrs[attr] == '') {
                return form_onAttrChange(container, widget, attr, attrs[attr], $this);
            }
            forEach(attrs[attr], function(n) {
                if (typeof(n) == "number") { // {'invisible': [1]}
                    return form_onAttrChange(container, widget, attr, n, $this);
                }
                if (row_is_editable) {
                    var $field = jQuery(this).bind('onAttrChange', partial(form_onAttrChange, container, widget, attr, attrs[attr], $this));
                    $field.change(partial(form_onAttrChange, container, widget, attr, attrs[attr], $this));
                }
                return form_onAttrChange(container, widget, attr, attrs[attr], $this);
            });
        }
    });
}

function form_onAttrChange(container, widgetName, attr, expr, elem) {

    var prefix = widgetName.slice(0, widgetName.lastIndexOf('/') + 1);
    var widget = openobject.dom.get(widgetName) || elem;

    var result = form_evalExpr(prefix, expr, elem);

    switch (attr) {
        case 'readonly':
            var editable = openobject.dom.get(prefix + '_terp_editable');
            if (editable && (editable.value == 0 || editable.value == 'False')) {
                // We are in 'non-editable' mode, so we force readonly = True
                // whatever readonly attrs result
                result = true;
            }
            form_setReadonly(container, widget, result);
            break;
        case 'required': form_setRequired(container, widget, result);
            break;
        case 'invisible': form_setVisible(container, widget, !result);
            break;
        default:
    }
}

function matchArray(val,eval_value){
    if (val.length != eval_value.length) { return false; }
    var val = val.sort(),
    eval_value = eval_value.sort();
    for (var i = 0; val[i]; i++) {
        if (val[i] !== eval_value[i]) { 
            return false;
        }
    }
    return true;
}

function form_find_field_in_context(prefix, field, ref_elem) {
    // try to find field in the context of reference element (ref_elem)
    var elem = null;
    if (ref_elem.parents('table.grid').length) {
        var parent = ref_elem.parents('tr.grid-row');
        elem = parent.find(idSelector(prefix + field));

        if (!elem || !elem.length) {
            var parent_selector = '[name='+prefix + field +']';
            elem = parent.find(parent_selector);
        }

        if (!elem || !elem.length) {
            // try getting with _terp_listfields/TABLE_ID/FIELD_NAME
            var parent_table_id = ref_elem.parents('table.grid')[0].id;
            if (parent_table_id && parent_table_id.match('_grid$')) {
                parent_table_id = parent_table_id.slice(0, parent_table_id.length - 5);
            }
            if (parent_table_id == '_terp_list') {
                // in case list name if '_terp_list' this means we're not inside a o2m/m2m fields,
                // and we no need need to prefix with parent_table_id name
                parent_table_id = ''
            } else {
                parent_table_id = parent_table_id + '/'
            }
            var parent_relative_fieldname = '[name=_terp_listfields/' + parent_table_id + prefix + field + ']';
            elem = parent.find(parent_relative_fieldname);
        }
    }
    if (!elem || !elem.length) {
        elem = jQuery(idSelector(prefix + field));
    }
    return elem;
}

function form_evalExpr(prefix, expr, ref_elem) {

    var stack = [];
    for (var i = 0; i < expr.length; i++) {

        var ex = expr[i];
        var elem = form_find_field_in_context(prefix, ex[0], ref_elem);

        if (ex.length==1) {
            stack.push(ex[0]);
            continue;
        }
        
        if (!elem || !elem.length)
            continue;

        var op = ex[1];
        var val = ex[2];

        var elem_value;
        if(elem.is(':input')) {
            elem_value = elem.val();
            var elem_kind = elem.attr('kind')
            var nan_pattern = /[^0-9]/g;
            if(elem_kind == 'float' || elem_kind == 'integer') {
                // extract sign and number from input value
                var sign = elem_value[0] == '-' ? '-' : '';
                var integer_part = elem_value.substring(sign.length), decimal_part = '';
                if (elem_kind == 'float') {
                    // split float integer and decimal parts on last non decimal char
                    var decimal_sep_position = integer_part.replace(nan_pattern, '.').lastIndexOf('.');
                    if (decimal_sep_position !== -1) {
                        decimal_part = '.' + integer_part.substring(decimal_sep_position+1);
                        integer_part = integer_part.substring(0, decimal_sep_position);
                    }
                }
                // remove all non-decimal chars and evalute string to get a real number
                integer_part = integer_part.replace(nan_pattern, '');
                elem_value = eval(sign + integer_part + decimal_part);
            }
        } else if(elem[0].nodeName == "TABLE"){
            prefix = $(elem).attr('id')
            elem_value = eval($(idSelector(prefix+"/_terp_ids")).val())
            res = matchArray(eval(val), elem_value)
            if(res){
                val = elem_value = true
            }else{
                val = true
                elem_value = false
            }
        } else {
            elem_value = elem.attr('value') || elem.text();
        }

        switch (op.toLowerCase()) {
            case '=':
            case '==':
                stack.push(elem_value == val);
                break;
            case '!=':
            case '<>':
                stack.push(elem_value != val);
                break;
            case '<':
                stack.push(elem_value < val);
                break;
            case '>':
                stack.push(elem_value > val);
                break;
            case '<=':
                stack.push(elem_value <= val);
                break;
            case '>=':
                stack.push(elem_value >= val);
                break;
            case 'in':
                stack.push(MochiKit.Base.findIdentical(val, elem_value) > -1);
                break;
            case 'not in':
                stack.push(MochiKit.Base.findIdentical(val, elem_value) == -1);
                break;
        }
    }

    for (var j=stack.length-1; j>-1; j--) {
        if(stack[j] == '|'){
            var result = stack[j+1] || stack[j+2];
            stack.splice(j, 3, result);
        }
    }
    // shouldn't find any `false` left at this point
    return stack.indexOf(false) == -1;
}

function form_setReadonly(container, fieldName, readonly) {

    var $field = typeof(fieldName) == "string" ? jQuery(idSelector(fieldName)) : jQuery(fieldName);

    if (!$field.length) {
        return;
    }

    var kind = $field.attr('kind');
    var field_id = $field.attr('id');
    var field_name = $field.attr('name');

    if (kind == 'boolean') {
        var boolean_field = jQuery('input#'+field_id+'_checkbox_');
        boolean_field.attr({'disabled':readonly, 'readOnly': readonly});
    }

    if (!kind &&
            jQuery(idSelector(field_id + '_id')) &&
            jQuery(idSelector(field_id + '_set')) &&
            jQuery(idSelector(field_id + '_id')).attr('kind') == "many2many") {
         Many2Many(field_id).setReadonly(readonly);
        return;
    }

    var type = $field.attr('type');

    if (!type && ($field.hasClass('item-group'))) {
        jQuery($field).find(':input')
                .toggleClass('readonlyfield', readonly)
                .attr({'disabled': readonly, 'readOnly': readonly});
        return;
    }
    
    if (type == 'hidden' && kind == 'many2one') {
        ManyToOne(field_id).setReadonly(readonly);
        $field = jQuery(idSelector(fieldName+'_text'));
    }
    
    $field.attr({'disabled':readonly, 'readOnly': readonly});

    if (readonly) {
        if ((type == 'button')) {
            $field.css("cursor", "default");
        } else {
            $field.removeAttr('href');
            $field.css("color", "gray");
        }
        
        $field.toggleClass('readonlyfield', type != 'button');
    } else {
        $field.removeClass('readonlyfield');
        $field.css('color', '');
    }

    if (!kind && (jQuery(idSelector(field_id+'_btn_')).length || jQuery(idSelector('_o2m'+field_id)).length)) { // one2many
        new One2Many(field_id).setReadonly(readonly);
        return;
    }

    if (kind == 'date' || kind == 'datetime' || kind == 'time') {
        jQuery(idSelector(field_name+'_trigger')).toggle(!readonly);
    }
}

function form_setRequired(container, field, required) {
    
    if (!field) {
        field = container;
    }
    var editable = getElement('_terp_editable').value;

    var $field = jQuery(idSelector(field));
    
    if (required == undefined){
        required =  $field.attr("fld_required") == "1" ? true : false; 
    }
    
    if (editable == 'True' && required) {
        $field.toggleClass('requiredfield', required);
    }
    else {
        $field.removeClass('requiredfield');
    }
    if(required) {
        $field.removeClass('readonlyfield');
    }
    $field.removeClass('errorfield');

    var kind = $field.attr('kind');
    var type = $field.attr('type');
    var name = $field.attr('name');

    if (type == 'hidden' && kind == 'many2one') {
        form_setRequired(container, name + '_text' , required);
    }
}

function form_setVisible(container, field, visible) {
    var $container = jQuery(container);
    if ($container.hasClass('notebook-page')) { // notebook page?
    
        var nb = container.parentNode.parentNode.notebook;

        if (!nb)  {
           MochiKit.Async.callLater(0, form_setVisible, container, field, visible);
           return;
        }

        var i = findIdentical(nb.pages, container);

        if (visible) {
            nb.show(i, false);
        } else {
            nb.hide(i);
        }

    } else {

        try {
            var $label = $container.prev('td.label');
            $container.toggle(visible);
            if ($label.length) {
                $label.toggle(visible);
            }
        }catch(e){}
    }
}

jQuery(document).ready(function(){
    form_hookContextMenu();
    form_hookStateChange();
    form_hookAttrChange();
});

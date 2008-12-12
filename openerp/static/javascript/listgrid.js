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

var ListView = function(name) {

    var elem = getElement(name);
    if (elem.__instance) {
        return elem.__instance;
    }

    var cls = arguments.callee;
    if (!(this instanceof cls)) {
        return new cls(name);
    }
  
    this.__init__(name);
}

ListView.prototype = {

    __init__: function(name){

        var prefix = name == '_terp_list' ? '' : name + '/';

        this.name = name;
        this.model = $(prefix + '_terp_model') ? $(prefix + '_terp_model').value : null;
        this.current_record = null;
    
        this.ids = getElement(prefix + '_terp_ids').value;

        var view_ids = getElement(prefix + '_terp_view_ids');
        var view_mode = getElement(prefix + '_terp_view_mode');
        var def_ctx = getElement(prefix + '_terp_default_get_ctx');
    
        this.view_ids = view_ids ? view_ids.value : null;
        this.view_mode = view_mode ? view_mode.value : null;
    
        // if o2m
        this.m2m = getElement(name + '_set');
        this.default_get_ctx = def_ctx ? def_ctx.value : null;

        // save the reference
        getElement(name).__instance = this;

        // store references of the container elements
        this.grid = getElement(this.name + '_grid');
        this.element = getElement(this.name);
    },

    checkAll: function(clear){

        clear = clear ? false : true;

        boxes = $(this.name).getElementsByTagName('input');
        forEach(boxes, function(box){
            box.checked = clear;
        });
    },
    
    getRecords: function() {
        var records = map(function(row){
            return parseInt(getNodeAttribute(row, 'record')) || 0;
        }, getElementsByTagAndClassName('tr', 'grid-row', this.name));
        
        return filter(function(rec){
            return rec;
        }, records);
    },

    getSelectedRecords: function() {
        return map(function(box){
            return box.value;
        }, this.getSelectedItems());
    },

    getSelectedItems: function() {
        return filter(function(box){
            return box.id && box.checked;
        }, getElementsByTagAndClassName('input', 'grid-record-selector', this.name));
    },

    getColumns: function(dom){
        dom = dom || this.name;
        var header = getElementsByTagAndClassName('tr', 'grid-header', dom)[0];
        
        return filter(function(c){
            return c.id ? true : false;
        }, getElementsByTagAndClassName('th', 'grid-cell', header));
    },

    makeArgs: function(){
        var args = {};
        var names = this.name.split('/');

        var values = ['id', 'ids', 'model', 'view_ids', 'view_mode', 'view_type', 
                      'domain', 'context', 'offset', 'limit', 'editable', 'selectable'];

        forEach(values, function(val){
            var key = '_terp_' + val;
            var elem = getElement(key);

            if (elem) args[key] = elem.value;
        });

        for(var i=0; i<names.length; i++){

            var name = names[i];
            var prefix = names.slice(0, i).join('/');

            prefix = prefix ? prefix + '/' + name : name;
            prefix = prefix + '/';

            forEach(values, function(val){
                var key = prefix + '_terp_' + val;
                var elem = getElement(key);

                if (elem) args[key] = elem.value;
            });
        }

        return args;
    }
}

// inline editor related functions
MochiKit.Base.update(ListView.prototype, {

    loadEditors: function(edit_inline, args) {

        var self = this;
        var req = Ajax.JSON.post('/listgrid/get_editor', args);

        req.addCallback(function(obj){
		
		    if(obj.source == '_terp_list')
			    prefix = '_terp_listfields';
		    else
            	prefix = '_terp_listfields' + '/' + obj.source;

            var tbl = self.grid;
            var tr = null;
            var idx = 1;
            
            var editor_row = getElementsByTagAndClassName('tr', 'editors', tbl)[0];
            var editors = self.adjustEditors(editor_row);
            
            if (editors.length > 0 && !editor_row.keyBound) {
                self.bindKeyEventsToEditors(editors);
                editor_row.keyBound = 1;
            }
            record_id = MochiKit.DOM.getNodeAttribute(editor_row, 'record');

            if(edit_inline != -1) {

                for (var i=0; i<tbl.rows.length; i++){
                    
                    var e = tbl.rows[i];
                    tr = MochiKit.DOM.getNodeAttribute(e, 'record') == edit_inline ? e : null;
                    if (tr) break;
                }

                if (tbl.last) {
                    tbl.last.style.display = '';
                }

                idx = findIdentical(tbl.rows, tr);
            }

            var tr_tmp = tbl.insertRow(idx);
            swapDOM(tr_tmp, editor_row);

            if(edit_inline == -1 && record_id == null){
                editor_row.style.display = '';
            } else if(edit_inline == -1 && record_id >= 0){
                if (tbl.last) {
                    tbl.last.style.display = '';
                }
                editor_row.style.display = '';
            } else {
                tr.style.display = 'none';
                editor_row.style.display = '';

                MochiKit.DOM.setNodeAttribute(editor_row, 'record', edit_inline);
            }

            elements = [];

            elements = elements.concat(getElementsByTagAndClassName('input', null, editor_row));
            elements = elements.concat(getElementsByTagAndClassName('select', null, editor_row));
           
            forEach(elements, function(f) {
                getElement(f).value = "";
            });

            for(var r in obj.res) {
                var id = prefix + '/' + r;
                var kind = 'char';
                var elem = getElement(id);

                if (elem) {                 
                    kind = MochiKit.DOM.getNodeAttribute(elem, 'kind');
                    type = MochiKit.DOM.getNodeAttribute(elem, 'type');
                    
                    if (kind ==  'many2one') {
                        val = obj.res[r] || ['', '']
                        elem.value = val[0];
                        try {
                            getElement(id + '_text').value = val[1];
                        } catch(e) {}
                    } else if ((kind = 'boolean') && (type = 'checkbox')) {
                        elem.value = obj.res[r];
                        try {
                            getElement(id + '_checkbox_').checked = obj.res[r];
                            getElement(id + '_checkbox_').value = obj.res[r];
                        } catch(e) {}
                    } else {
                        elem.value = obj.res[r];
                    }
                }
            }

            tbl.last = tr;
            var first = getElementsByTagAndClassName(null, 'listfields', this.name)[0] || null;
            if (first) {
                first.focus();
                first.select();
            }
        });
    },

    adjustEditors: function(newlist){

        var editors = this.getEditors(false, newlist);

        forEach(editors, function(e) {
            // disable autocomplete (Firefox < 2.0 focus bug)
            setNodeAttribute(e, 'autocomplete', 'OFF');
        });

        if (/MSIE/.test(navigator.userAgent)){
            return editors;
        }

        var widths = {};
        
        // set the column widths of the newlist
        forEach(this.getColumns(), function(c){
            widths[c.id] = parseInt(c.offsetWidth) - 8;
        });
     
        forEach(this.getColumns(newlist), function(c){
            c.style.width = widths[c.id] + 'px';
        });

        var widths = {};
        forEach(this.getEditors(), function(e){
            widths[e.id] = parseInt(e.offsetWidth);
        });

        return editors;
    },

    bindKeyEventsToEditors: function(editors){
        var self = this;
        var editors = filter(function(e){
            return e.type != 'hidden' && !e.disabled
        }, editors);

        forEach(editors, function(e){
            connect(e, 'onkeydown', self, self.onKeyDown);
            addElementClass(e, 'listfields');
        });
    },

    cancel_editor: function(row){

        var tbl = this.grid;
        var editor_cancel = getElementsByTagAndClassName('tr', 'editors', tbl)[0];

        hideElement(editor_cancel);

        if(tbl.last) {
            MochiKit.DOM.setNodeAttribute(editor_cancel, 'record', 0);
            tbl.last.style.display = '';
        }
    },

    save_editor: function(row){
        this.save(MochiKit.DOM.getNodeAttribute(row, 'record'));
    },

    getEditors: function(named, dom){
        var editors = [];
        var dom = dom ? dom : this.name;

        editors = editors.concat(getElementsByTagAndClassName('input', null, dom));
        editors = editors.concat(getElementsByTagAndClassName('select', null, dom));
        editors = editors.concat(getElementsByTagAndClassName('textarea', null, dom));

        return filter(function(e){
            name = named ? e.name : e.id;
            return name &&  name.indexOf('_terp_listfields') == 0;
        }, editors);
    },

    makeRow: function(rec_id) {

        if (Ajax.COUNT > 0) {
            return callLater(1, bind(this.makeRow, this), rec_id);
        }
	
	    var self = this;
	    var tbl = this.grid;
	
	    var editor_row = getElementsByTagAndClassName('tr', 'editors', tbl)[0];
		
	    record_id = MochiKit.DOM.getNodeAttribute(editor_row, 'record');
	
	    if(record_id > 0) {
	        rec_id = record_id;
	    }
	
	    var elem = [];
	    var elements = [];
	    var tds = [];
	    var parent_tag = [];
	
	    elem = self.getColumns();
	
	    elements = elements.concat(getElementsByTagAndClassName('input', null, editor_row));
	    elements = elements.concat(getElementsByTagAndClassName('select', null, editor_row));
	
	    var check_box = MochiKit.DOM.INPUT({
                    'id': self.name  + '/' +  rec_id , 
                    'class': 'checkbox grid-record-selector', 
                    'type': 'checkbox', 
                    'name': self.name, 
                    'value': rec_id});

	    var check_td = MochiKit.DOM.TD({'class': 'grid-cell selector'}, check_box);
	    tds.push(check_td);
	
	    var td_edit = MochiKit.DOM.TD({'class': 'grid-cell selector', 'style': 'text-align: center; padding: 0px;'});
        var edit = MochiKit.DOM.IMG({
                    'class': 'listImage', 
                    'border': '0', 
                    'src': '/static/images/edit_inline.gif', 
                    'onclick': 'new ListView(\''+ this.name +'\').edit('+ rec_id +')'});
        
        MochiKit.DOM.appendChildNodes(td_edit, edit);
        tds.push(td_edit);
	
	    forEach(elem, function(e) {
		    elem_id = getElement(e).id.replace('grid-data-column', '_terp_listfields');
		    temp_id = elem_id;
		
		    for(var i=0; i<elements.length; i++) {
			    if(getElement(elements[i]).type != 'hidden') {
				    if(elem_id == getElement(elements[i]).id || (elem_id + '_text') == getElement(elements[i]).id || (elem_id + '_checkbox_') == getElement(elements[i]).id){
					    parent_tag = getFirstParentByTagAndClassName(elements[i], 'td', 'grid-cell');
					    value = getElement(elements[i]).value;
					
					    if (parent_tag.className.indexOf('selection') != -1){
					       value = getElement(elements[i]).options[getElement(elements[i]).selectedIndex].text; 
					    }
					
					    if (parent_tag.className.indexOf('boolean') != -1){
                            if (getElement(elements[i]).value == 1) {
                                value = 'Yes';
                            } else {
                                value = 'No';
                            } 
                        }
					
					    if(parent_tag.className.indexOf('many2one') != -1 || i == 0){
					        var column = MochiKit.DOM.TD({'class': parent_tag.className});
					     
					        if(i==0) {
					           var anchor = MochiKit.DOM.A({
                                                       'onclick': 'do_select(\'' + rec_id + '\', \'' + self.name + '\'); return false;', 
                                                       'href': 'javascript: void(0)'}, value);
					        }
					        else {
					            var m2o_id = getElement(temp_id).value;
					            var relation = getNodeAttribute(getElement(elements[i]), 'relation');
					            
					            var action = '/form/view?model=' + relation + '&id= ' + m2o_id;
					            
					            var anchor = MochiKit.DOM.A({'href': 'javascript: void(0)'}, value);
					            
					            MochiKit.DOM.setNodeAttribute(anchor, 'href', action);
					        }
					        MochiKit.DOM.appendChildNodes(column, anchor);
					        tds.push(column);
					    }
					    else if(getElement(elements[i]).id == '_terp_listfields/sequence') {
                            
					        var column = MochiKit.DOM.TD({'class': parent_tag.className});
					        var span_val = MochiKit.DOM.SPAN(value);
					        					    
                            var span_up = MochiKit.DOM.SPAN({'class': 'grid-cell selector'});
                            var img_up = MochiKit.DOM.IMG({'id': rec_id + '_moveup',
                                                        'seq': tbl.__seq, 
                                                        'class': 'listImage', 
                                                        'title': 'Move Up',
                                                        'border': '0',
                                                        'src': '/static/images/up.png',
                                                        'onclick' : 'new ListView(\'' + self.name + '\').moveUp(' + rec_id + ')'});
                            
                            MochiKit.DOM.appendChildNodes(span_up, img_up);
                                                                                
                            var img_down = MochiKit.DOM.IMG({'id': rec_id + '_movedown',
                                                        'seq': tbl.__seq,
                                                        'class': 'listImage',
                                                        'title': 'Move Down',
                                                        'border': '0',
                                                        'src': '/static/images/down.png',
                                                        'onclick': 'new ListView(\'' + self.name + '\').moveDown(' + rec_id + ')'});
                                                        
                            var span_down = MochiKit.DOM.SPAN({'class': 'grid-cell selector'});
                            MochiKit.DOM.appendChildNodes(span_down, img_down);
                            
                            MochiKit.DOM.appendChildNodes(column, span_val, span_up, span_down);
                            
                            tds.push(column);
                        }					
					    else {
					        var col = MochiKit.DOM.TD({'class': parent_tag.className}, value);
					        tds.push(col);
					    }
				    }
			    }
		    }
	    });
	
	    var td_del = MochiKit.DOM.TD({'class': 'grid-cell selector', 'style': 'text-align: center; padding: 0px;'});
	    var del = MochiKit.DOM.IMG({'class': 'listImage', 
                'border': '0', 
                'src': '/static/images/delete_inline.gif', 
                'onclick': 'new ListView(\''+ this.name +'\').remove('+ rec_id +')'});
	
	    MochiKit.DOM.appendChildNodes(td_del, del);	
	    tds.push(td_del);
        
	    if(record_id > 0) {
		    var tr = MochiKit.DOM.TR({'class': 'grid-row', 'record': record_id}, tds);
		
		    idx = findIdentical(tbl.rows, editor_row);
            swapDOM(tbl.last, tr);
        	
		    tr.style.display = '';
		    editor_row.style.display = 'none';
            MochiKit.DOM.setNodeAttribute(editor_row, 'record', 0);
	    }
	    else {
	        var idx = 1;
		    var tr = MochiKit.DOM.TR({'class': 'grid-row', 'record': rec_id}, tds);
            
            var tr_tmp = tbl.insertRow(idx + 1);
            swapDOM(tr_tmp, tr);
		
		    self.create();
	    }
    }

});

// pagination & reordering
MochiKit.Base.update(ListView.prototype, {

    moveUp: function(id) {

        var self = this;
        var args = {};
        
        sq = MochiKit.DOM.getNodeAttribute($(id +'_moveup'), 'seq');
        self.seq = eval ('(' + sq + ')');
        
        args['_terp_model'] = this.model;
        args['_terp_ids'] = this.ids;
        
        if((self.seq['prev'][1] == 0) && (self.seq['current'][1] == 0)) {
            var req = Ajax.JSON.post('/listgrid/assign_seq', args);
            
            req.addCallback(function(){      
                self.reload();        
            });
        }
        
        if (self.seq['prev'][0]) {
            args['_terp_prev_id'] = self.seq['prev'][0];
            args['_terp_prev_seq'] = self.seq['prev'][1];  
        }
        
        if (self.seq['current'][0]) {
            args['_terp_cur_id'] = self.seq['current'][0];
            args['_terp_cur_seq'] = self.seq['current'][1];
        }
        
        if (self.seq['prev'][0]) {
            var req = Ajax.JSON.post('/listgrid/moveUp', args);
            
            req.addCallback(function(){      
                self.reload();        
            });
        }
    },

    moveDown: function(id) {
        var self = this;
        var args = {};
        
        sq = MochiKit.DOM.getNodeAttribute($(id +'_movedown'), 'seq');
        self.seq = eval ('(' + sq + ')');
        
        args['_terp_model'] = this.model;
        
        if((self.seq['next'][1] == 0) && (self.seq['current'][1] == 0)) {
            var req = Ajax.JSON.post('/listgrid/assign_seq', args);
            
            req.addCallback(function(){      
                self.reload();        
            });
        }
        
        if (self.seq['next'][0]) {
            args['_terp_next_id'] = self.seq['next'][0];
            args['_terp_next_seq'] = self.seq['next'][1];
        }
        
        if (self.seq['current'][0]) {
            args['_terp_cur_id'] = self.seq['current'][0];
            args['_terp_cur_seq'] = self.seq['current'][1];
        }
        
        if (self.seq['next'][0]) {
            var req = Ajax.JSON.post('/listgrid/moveDown', args);
            
            req.addCallback(function(){      
                self.reload();        
            });
        }
    }
});

// event handlers
MochiKit.Base.update(ListView.prototype, {

    onKeyDown: function(evt){
        var key = evt.key();
        var src = evt.src();

        if (!(key.string == "KEY_TAB" || key.string == "KEY_ENTER" || key.string == "KEY_ESCAPE")) {
            return;
        }

        if (key.string == "KEY_ESCAPE"){
            evt.stop();
            this.cancel_editor();
            return;
        }

        if (key.string == "KEY_ENTER"){

            if (hasElementClass(src, "m2o")){

                var k = src.id;
                k = k.slice(0, k.length - 5);

                if (src.value && !getElement(k).value){
                    return;
                }
            }

            if (src.onchange) {
                src.onchange();
            }
            
            var tbl = this.grid;
            var editor_save = getElementsByTagAndClassName('tr', 'editors', tbl)[0];
            
            evt.stop();
            record = MochiKit.DOM.getNodeAttribute(editor_save, 'record');
            
            this.save(record);
            
            return;
        }

        var editors = getElementsByTagAndClassName(null, 'listfields', this.name);

        var first = editors.shift();
        var last = editors.pop();

        if (src == last){
            evt.stop();
            first.focus();
            first.select();
        }
    },

    onButtonClick: function(name, btype, id, sure, context){

        if (sure && !confirm(sure)){
            return;
        }
        
        var self = this;
        var prefix = this.name == '_terp_list' ? '' : this.name + '/';

        name = name.split('.').pop();
        
        var params = {
            _terp_model : this.model,
            _terp_id : id,
            _terp_button_name : name,
            _terp_button_type : btype
        }

        var req = eval_domain_context_request({source: this.name, context : context || '{}'});
        req.addCallback(function(res){
            params['_terp_context'] = res.context;
            var req = Ajax.JSON.post('/listgrid/button_action', params);
            req.addCallback(function(obj){
                if (obj.error){
                    return alert(obj.error);
                }

                if (obj.reload) {
                    window.location.reload();
                } else
                    self.reload();
            });
        });
    }
});

// standard actions
MochiKit.Base.update(ListView.prototype, {

    create: function(){

        var tbl = this.grid;
        var editor = getElementsByTagAndClassName('tr', 'editors', tbl)[0];

        MochiKit.DOM.setNodeAttribute(editor, 'record', 0);
        
        this.edit(-1);
    },

    edit: function(edit_inline){
        var self = this;
        var args = this.makeArgs();
        
        var tbl = this.grid;

        tbl.__seq = MochiKit.DOM.getNodeAttribute($(edit_inline +'_moveup'), 'seq') || "{}";
        
        // add args
        args['_terp_source'] = this.name;
        args['_terp_edit_inline'] = edit_inline;
        
        if (this.name == '_terp_list') {
            args['_terp_search_domain'] = $('_terp_search_domain').value;
        }
        
        if (!this.default_get_ctx) {
            return self.loadEditors(edit_inline, args)
        }

        var req = eval_domain_context_request({source: this.name, context : this.default_get_ctx});
        
        req.addCallback(function(res){
            args['_terp_context'] = res.context;
            self.loadEditors(edit_inline, args);
        });
    },

    save: function(id){

        if (Ajax.COUNT > 0) {
            return callLater(1, bind(this.save, this), id);
        }

        var parent_field = this.name.split('/');
        var data = getFormData(true);
        var args = {};

        for(var k in data) {
            if (k.indexOf(this.name + '/') == 0 || this.name == '_terp_list') {
                args[k] = data[k];
            }
        }

        var prefix = this.name == '_terp_list' ? '' : this.name + '/';

        args['_terp_id'] = id ? id : -1;
        args['_terp_ids'] = $(prefix + '_terp_ids').value;
        args['_terp_model'] = this.model;

        if (parent_field.length > 0){
            parent_field.pop();
        }

        parent_field = parent_field.join('/');
        parent_field = parent_field ? parent_field + '/' : '';

        args['_terp_parent/id'] = $(parent_field + '_terp_id').value;
        args['_terp_parent/model'] = $(parent_field + '_terp_model').value;
        args['_terp_parent/context'] = $(parent_field + '_terp_context').value;
        args['_terp_source'] = this.name;

        var self = this;
        var req= Ajax.JSON.post('/listgrid/save', args);

        req.addCallback(function(obj){
            if (obj.error){
                alert(obj.error);

                if (obj.error_field) {
                    var fld = getElement('_terp_listfields/' + obj.error_field);

                    if (fld && getNodeAttribute(fld, 'kind') == 'many2one')
                        fld = getElement(fld.id + '_text');

                    if (fld) {
                        fld.focus();
                        fld.select();
                    }
                }
            } else {

                $(prefix + '_terp_id').value = obj.id;
                $(prefix + '_terp_ids').value = obj.ids;

                // TODO: make rows for all newly created rows
                self.makeRow(obj.id);
             }
         });
    },

    remove: function(ids){

        var self = this;
        var args = {};
        
        if(!ids) {
            var ids = this.getSelectedRecords();
            if(ids.length > 0){
                ids = '[' + ids.join(', ') + ']';
            }
        }
        
        if (ids.length == 0) {
            return alert('You must select at least one record.');
        }
        else if (!confirm('Do you realy want to delete record(s) ?')) {
            return false;
        }
        
        args['_terp_model'] = this.model;
        args['_terp_ids'] = ids;

        var req = Ajax.JSON.post('/listgrid/remove', args);

        req.addCallback(function(obj){
            if (obj.error){
                alert(obj.error);
            } else {
                self.reload();
            }
        });
    },

    go: function(action){
        
        if (Ajax.COUNT > 0){
            return;
        }

        var prefix = this.name == '_terp_list' ? '' : this.name + '/';

        var o = $(prefix + '_terp_offset');
        var l = $(prefix + '_terp_limit');
        var c = $(prefix + '_terp_count');

        var ov = o.value ? parseInt(o.value) : 0;
        var lv = l.value ? parseInt(l.value) : 0;
        var cv = c.value ? parseInt(c.value) : 0;

        switch(action) {
            case 'next':
                o.value = ov + lv;
                break;
            case 'previous':
                o.value = lv > ov ? 0 : ov - lv;
                break;
            case 'first':
                o.value = 0;
                break;
            case 'last':
                o.value = cv - (cv % lv);
                break;
        }

        this.reload();
    },

    reload: function(edit_inline){

        var self = this;
        var args = this.makeArgs();

        // add args
        args['_terp_source'] = this.name;
        args['_terp_edit_inline'] = edit_inline;

        if (this.name == '_terp_list') {
            args['_terp_search_domain'] = $('_terp_search_domain').value;
        }

        var req = Ajax.JSON.post('/listgrid/get', args);
        req.addCallback(function(obj){

            var _terp_id = $(self.name + '/_terp_id') || $('_terp_id');
            var _terp_ids = $(self.name + '/_terp_ids') || $('_terp_ids');
            var _terp_count = $(self.name + '/_terp_count') || $('_terp_count');
            
            if(obj.ids) {
                _terp_id.value = obj.ids[0];
                _terp_ids.value = '[' + obj.ids.join(',') + ']';
                _terp_count.value = obj.count;
            }

            var d = DIV();
            d.innerHTML = obj.view;

            var newlist = d.getElementsByTagName('table')[0];
            var editors = self.adjustEditors(newlist);
            
            if (editors.length > 0)
                self.bindKeyEventsToEditors(editors);
                
            self.current_record = edit_inline;

            swapDOM(self.name, newlist);

            var ua = navigator.userAgent.toLowerCase();

            if ((navigator.appName != 'Netscape') || (ua.indexOf('safari') != -1)) {
                // execute JavaScript
                var scripts = getElementsByTagAndClassName('script', null, newlist);
                forEach(scripts, function(s){
                    eval(s.innerHTML);
                });
            }

            // set focus on the first field
            var first = getElementsByTagAndClassName(null, 'listfields', this.name)[0] || null;
            if (first) {
                first.focus();
                first.select();
            }
        });
    }

});

// export/import functions
MochiKit.Base.update(ListView.prototype, {

    exportData: function(){
        
        var ids = this.getSelectedRecords();
        
        if (ids.length == 0) {
            ids = this.getRecords();
        }
        
        ids = '[' + ids.join(',') + ']';
        
        openWindow(getURL('/impex/exp', {_terp_model: this.model, 
                                         _terp_source: this.name, 
                                         _terp_search_domain: $('_terp_search_domain').value, 
                                         _terp_ids: ids,
                                         _terp_view_ids : this.view_ids,
                                         _terp_view_mode : this.view_mode}));
    },

    importData: function(){
        openWindow(getURL('/impex/imp', {_terp_model: this.model,
                                         _terp_source: this.name,
                                         _terp_view_ids : this.view_ids,
                                         _terp_view_mode : this.view_mode}));
    }        
});

// vim: ts=4 sts=4 sw=4 si et


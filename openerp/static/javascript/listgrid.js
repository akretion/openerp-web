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
    }

});

// pagination & reordering
MochiKit.Base.update(ListView.prototype, {

    moveUp: function(id) {

        var self = this;
        var args = {};
        
        args['_terp_model'] = this.model;
        args['_terp_ids'] = this.ids;
        args['_terp_id'] = id;
        
        var req = Ajax.JSON.post('/listgrid/moveUp', args);
        req.addCallback(function(){      
            self.reload();        
        });        
    },

    moveDown: function(id) {

        var self = this;
        var args = {};
        
        args['_terp_model'] = this.model;
        args['_terp_ids'] = this.ids;
        args['_terp_id'] = id;
        
        var req = Ajax.JSON.post('/listgrid/moveDown', args);
        req.addCallback(function(){      
            self.reload();        
        });
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
            return this.reload();
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
            
            evt.stop();
            return this.save(this.current_record);
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
        this.edit(-1);
    },

    edit: function(edit_inline){
        this.reload(edit_inline);
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

                self.reload(id > 0 ? null : -1);
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

        if (Ajax.COUNT > 0) {
            return callLater(1, bind(this.reload, this), edit_inline);
        }

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
            var first = getElementsByTagAndClassName(null, 'listfields', self.name)[0] || null;
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


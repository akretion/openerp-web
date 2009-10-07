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

var TreeGrid = function(elem, options){
    this.__init__(elem, options);
}

TreeGrid.prototype = {
    
    __init__ : function(elem, options) {
        
        this.id = MochiKit.DOM.getElement(elem).id;
        
        this.options = MochiKit.Base.update({
            'showheaders': true,
            'expandall' : false,
            'onselect' : function(evt, node){},
            'onbuttonclick' : function(evt, node){},
            'onheaderclick' : function(evt, header){},
            'linktarget': null
        }, options || {});
        
        // a dummy root node
        this.rootNode = null;
        
        // selection info
        this.selection = [];
        this.selection_last = null;
        
        // ajax call counter
        this._ajax_counter = 0;
        
        // references to ajax url and params
        this.ajax_url = null;
        this.ajax_params = {};
    },
    
    setHeaders : function(headers/*, params */) {
        
        this.headers = headers;
        
        if (typeof(headers) == 'string'){
            
           var self = this;
           var req = Ajax.JSON.post(headers, arguments[1]);
           
           self._ajax_counter += 1;
           
           req.addCallback(function(obj){
               self.headers = obj.headers;
           });
           
           req.addBoth(function(obj){
               self._ajax_counter -= 1;
           });
           
        };
    },
    
    setRecords : function(records/*, params */) {
        
        if (!this.headers) {
            return;
        }
        
        this.records = records;
        
        if (typeof(records) == 'string'){
            
            this.ajax_url = records;
            this.ajax_params = arguments[1] || {};
            
            var self = this;
            var req = Ajax.JSON.post(this.ajax_url, this.ajax_params);
            
            var div = DIV({id: this.id}, _("Loading..."));
            MochiKit.DOM.swapDOM(this.id, div);
           
            self._ajax_counter += 1;
           
            req.addCallback(function(obj){
                self.records = obj.records;
                MochiKit.Signal.signal(self, 'onDataLoad', self, null);
            });
           
            req.addBoth(function(obj){
                self._ajax_counter -= 1;
            });
           
        };
        
    },
    
    render : function(){
        
        // wait till ajax calls finish
        if (this._ajax_counter > 0) {
            return MochiKit.Async.callLater(0.01, MochiKit.Base.bind(this.render, this));
        }
        
        this.thead = MochiKit.DOM.THEAD({'class': 'tree-head'});
        this.tbody = MochiKit.DOM.TBODY({'class': 'tree-body'});
        this.table = MochiKit.DOM.TABLE({id: this.id, 'class': 'tree-grid'}, this.thead, this.tbody);
        
        if (this.options.showheaders) {
            this._makeHeader();
        }
        
        this._makeBody();
        
        MochiKit.DOM.swapDOM(this.id, this.table);
    },
    
    reload : function() {
        this.rootNode.__delete__();
        this.setRecords(this.ajax_url || this.records, this.ajax_params);
        this.render();
    },
    
    createNode : function(record) {
        return new TreeNode(this, record);  
    },
    
    _makeHeader : function(){
        
        var tr = MochiKit.DOM.TR({'class':'header'});
    
        for(var i in this.headers){
            
            var header = this.headers[i];
            var th = MochiKit.DOM.TH(null, header.string);
    
            MochiKit.DOM.setNodeAttribute(th, 'title', header.help ? header.help : '');
            MochiKit.DOM.setNodeAttribute(th, 'class', header.type);
            MochiKit.DOM.setNodeAttribute(th, 'width', header.width);
            MochiKit.DOM.setNodeAttribute(th, 'align', header.align);
            
            if (this.options.onheaderclick){
               th.onclick = MochiKit.Base.bind(MochiKit.Base.partial(this._onHeaderClick, header), this);
               th.style.cursor = 'pointer';
            }
    
            MochiKit.DOM.appendChildNodes(tr, th);
        }
    
        MochiKit.DOM.appendChildNodes(this.thead, tr);
    },
    
    _makeBody : function() {
        this.rootNode = this.createNode({children: this.records});
        this.rootNode.expand(this.options.expandall ? true : false);
    },
    
    _onHeaderClick : function(header) {
        var evt = arguments[1] || window.event;
        this.options.onheaderclick(new MochiKit.Signal.Event(evt.target || evt.srcElement, evt), header);
    }
}

var TreeNode = function(tree, record) {
    this.__init__(tree, record);
}

TreeNode.prototype = {

    __init__ : function(tree, record) {
        
        this.tree = tree;
        this.record = record; 
        
        this.name = record['id'] || null;
        
        this.element = null;   // the row (tr) element
        this.element_a = null; // the link element
        this.element_b = null; // the expand/collapse element
        this.element_i = null; // the image
        
        this.childNodes = [];
        
        this.parentNode = null;
        
        this.firstChild = null;
        this.lastChild = null;
        this.previousSibling = null;
        this.nextSibling = null;
        
        this.hasChildren = record.children ? record.children.length > 0 : false;
                
        this.expanded = false;
    },
    
    __delete__ : function() {
        

        while(this.childNodes.length > 0) {
            this.childNodes[0].__delete__();
        }
        
        if (!this.element) {
            return;
        }
        
        var pn = this.parentNode;
        var idx = MochiKit.Base.findIdentical(pn.childNodes, this);
        
        pn.childNodes.splice(idx,1);
        
        if (pn.firsChild == this) {
            pn.firstChild = pn.childNodes[0] || null;
        }
        
        if (pn.lastChild == this) {
            pn.lastChild = pn.childNodes[pn.childNodes.length-1] || null;
        }
        
        if (this.previousSibling) {
            this.previousSibling.nextSibling = this.nextSibling;
        }
        
        if (this.nextSibling) {
            this.nextSibling.previousSibling = this.previousSibling;
        }
        
        this.tree.selection.splice(MochiKit.Base.findIdentical(this.tree.selection, this),1);
        this.tree.selection_last = this.selection_last == this ? null : this.selection_last;
        
        var table = this.tree.table;
        table.deleteRow(MochiKit.Base.findIdentical(table.rows, this.element));

        if (this.element) {
            MochiKit.Signal.disconnect(this.eventOnKeyDown);
            MochiKit.Signal.disconnect(this.eventOnClick);
            MochiKit.Signal.disconnect(this.eventOnDblClick);
        }
        
        if (pn.childNodes.length == 0 && pn.element_b) {
            pn.collapse();
            pn.hasChildren = false;
            pn.element_b.className = 'indent';
        }
    },
    
    __repr__ : function(){
        return '<TreeNode ' + this.name + '>';
    },
    
    createDOM : function() {

        this.element = MochiKit.DOM.TR({'class' : 'row'});
        this.element.style.display = this.parentNode ? (this.parentNode.expanded ? "" : "none") : "";
        
        var record = this.record;
        var indent = this.getPath().length - 1;

        for (var i in this.tree.headers){
            
            var header = this.tree.headers[i];
            
            var key = header.name;
            var value = this.record.items[key];
            
            var td = MochiKit.DOM.TD({'class': header.type || null, 'width' : header.width || null});
            
            if (i == 0) { // first column
    
                var tds = [];
    
                for(var i = 0; i < indent; i++){
                    tds.push(SPAN({'class' : 'indent'}));
                }
                
                var arrow = SPAN({'class': this.hasChildren ? 'expand' : 'indent'});
                this.element_b = arrow;

                arrow.onclick = MochiKit.Base.bind(function(){
                    this.toggle();
                }, this);
                    
                tds.push(arrow);
                
                if (record.icon) {
                    this.element_i = IMG({'src': record.icon, 'align': 'left', 'width' : 16, 'height' : 16});
                    tds.push(this.element_i);
                }
    
                value = A({'href': 'javascript: void(0)'}, value);
                this.element_a = value;
                
                this.eventOnKeyDown = MochiKit.Signal.connect(value, 'onkeydown', this, this.onKeyDown);
    
                if (record.action) {
                    MochiKit.DOM.setNodeAttribute(value, 'href', record.action);
                } else {
                    
                    value.onclick = MochiKit.Base.bind(function(){
                        this.toggle();
                        return false;
                    }, this);
                }
    
                if (record.target) {
                    MochiKit.DOM.setNodeAttribute(value, 'target', record.target);
                } else if (this.tree.options.linktarget) {
                    MochiKit.DOM.setNodeAttribute(value, 'target', this.tree.options.linktarget);
                }
                
                if(record.required) {
                    MochiKit.DOM.setNodeAttribute(value, 'class', 'requiredfield');
                }
    
                tds.push(value);
                tds = map(function(x){return TD(null, x)}, tds);
    
                value = TABLE({'class': 'tree-field', 'cellpadding': 0, 'cellspacing': 0}, 
                           TBODY(null, TR(null, tds)));
            }
            
            if (i > 0) {
                
                if (header.type == 'url' && value) {
                    value = MochiKit.DOM.A({href: record.action || value, target: record.target || '_blank'}, value);    
                }
                
                if (header.type == 'email' && value) {
                    value = MochiKit.DOM.A({href: 'mailto:' + (record.action || value), target: record.target || '_blank'}, value);    
                }
                
                if (header.type == 'image' && value) {
                    value = MochiKit.DOM.IMG({name: header.name, src: value, style: 'cursor: pointer'});
                    value.onclick = MochiKit.Base.bind(this.onButtonClick, this);
                }
                
                if (header.type == 'button' && value) {
                    value = MochiKit.DOM.BUTTON({name: header.name, style: 'cursor: pointer'}, value);
                    value.onclick = MochiKit.Base.bind(this.onButtonClick, this);
                }
                
            }

            MochiKit.DOM.appendChildNodes(td, value);
            MochiKit.DOM.appendChildNodes(this.element, td);
        }
        
        // register OnClick, OnDblClick event
        this.eventOnClick = MochiKit.Signal.connect(this.element, 'onclick', this, this.onSelect);
        this.eventOnDblClick = MochiKit.Signal.connect(this.element, 'ondblclick', this, this.toggle);
        
        return this.element;
    },
    
    updateDOM : function(record) {
        
        MochiKit.Base.update(this.record, record || {});
        
        var record = this.record;

        for (var i in this.tree.headers){
            
            var header = this.tree.headers[i];
            
            var key = header.name;
            var value = record.items[key];
            
            var td = this.element.cells[i];
            
            if (i == 0) { // first column                
                
                if (record.icon && this.element_i) {
                    this.element_i.src = record.icon;
                }
                
                this.element_a.innerHTML = MochiKit.DOM.escapeHTML(value);
                
                if (record.action) {
                    MochiKit.DOM.setNodeAttribute(this.element_a, 'href', getURL(record.action));
                }
                
                if (record.target) {
                    MochiKit.DOM.setNodeAttribute(this.element_a, 'target', getURL(record.target));
                }
                
                if(record.required) {
                    MochiKit.DOM.setNodeAttribute(this.element_a, 'class', 'requiredfield');
                }

            }
            
            if (i > 0) {
                
                if (header.type == 'url') {

                    var a = MochiKit.DOM.getElementsByTagAndClassName('a', null, td)[0];
                    
                    MochiKit.DOM.setNodeAttribute(a, 'href', value);
                    MochiKit.DOM.setNodeAttribute(a, 'target', record.target || '_blank');
                    
                    a.innerHTML = MochiKit.DOM.escapeHTML(value);    
                }
                
                if (header.type == 'email') {
                    
                    var a = MochiKit.DOM.getElementsByTagAndClassName('a', null, td)[0];
                    
                    MochiKit.DOM.setNodeAttribute(a, 'href', 'mailto:' + value);
                    MochiKit.DOM.setNodeAttribute(a, 'target', record.target || '_blank');
                    
                    a.innerHTML = MochiKit.DOM.escapeHTML(value);    
                }
                
                if (header.type == 'image') {
                    var i = MochiKit.DOM.getElementsByTagAndClassName('img', null, td)[0];
                    MochiKit.DOM.setNodeAttribute(a, 'src', value);
                }
                
                if (header.type == 'button') {
                    var b = MochiKit.DOM.getElementsByTagAndClassName('button', null, td)[0];
                    a.innerHTML = MochiKit.DOM.escapeHTML(value);
                }
            }
        }
        
        return this.element;
    },    
    
    onKeyDown : function(evt) {
        
        var key = evt.event().keyCode;
        
        switch (key) {
            
            case 37: //"KEY_ARROW_LEFT":
            
                if (this.expanded) {
                    this.collapse();
                } else if (this.parentNode.element){
                    this.parentNode.onSelect(evt);
                }
                return evt.stop();
                
            case 39: //"KEY_ARROW_RIGHT":
            
                if (!this.expanded) {
                    this.expand();
                } else if (this.firstChild) {
                    this.firstChild.onSelect(evt);
                }
                return evt.stop();
                
            case 38: //"KEY_ARROW_UP":
                
                var visible_nodes = this.tree.rootNode.getAllChildren();
                
                visible_nodes = MochiKit.Base.filter(function(node){
                    return node.element && node.element.style.display != "none";
                }, visible_nodes);
                
                visible_nodes = visible_nodes.slice(0, MochiKit.Base.findIdentical(visible_nodes, this));
                
                if (visible_nodes.length > 0){
                    visible_nodes[visible_nodes.length-1].onSelect(evt);
                }

                return evt.stop();
            
            case 40: //"KEY_ARROW_DOWN":
                
                var visible_nodes = this.tree.rootNode.getAllChildren();
                
                visible_nodes = MochiKit.Base.filter(function(node){
                    return node.element && node.element.style.display != "none";
                }, visible_nodes);
                
                visible_nodes = visible_nodes.slice(MochiKit.Base.findIdentical(visible_nodes, this)+1);
                
                if (visible_nodes.length > 0){
                    visible_nodes[0].onSelect(evt);
                }
            
                return evt.stop();
                
            default:
                return;
        }
        
    },
    
    onSelect : function(evt) {
        
        if (this.tree._ajax_counter > 0) {
            return;
        }
        
        var trg = evt ? evt.target() : this.element;
    
        if (MochiKit.Base.findValue(['collapse', 'expand', 'loading'], trg.className) > -1){
            return;
        }
        
        var tree = this.tree;
        var src = this.element;
        
        var ctr = evt ? evt.modifier().ctrl : null;
        var sft = evt ? evt.modifier().shift : null;
        
        if (this.element_a) {
            this.element_a.focus();
        }
        
        forEach(tree.selection, function(node){
            MochiKit.DOM.removeElementClass(node.element, "selected");
        });
    
        if (ctr) {
            if (MochiKit.Base.findIdentical(tree.selection, this) == -1){
                tree.selection.push(this);
            } else {
                tree.selection.splice(MochiKit.Base.findIdentical(tree.selection, this), 1);
            }
        } else if (sft) {
    
            var nodes = tree.rootNode.getAllChildren();
            nodes = MochiKit.Base.filter(function(node){
                return node.element.style.display != 'none';
            }, nodes);
    
            var last = tree.selection_last;
            last = last ? last : this;
    
            var begin = MochiKit.Base.findIdentical(nodes, this);
            var end = MochiKit.Base.findIdentical(nodes, last);
    
            tree.selection = begin > end ? nodes.slice(end, begin+1) : nodes.slice(begin, end+1);
    
        } else {
            tree.selection = [this];
        }
    
        if (!sft){
            tree.selection_last = tree.selection[tree.selection.length-1];
        }
    
        forEach(tree.selection, function(node){
            MochiKit.DOM.addElementClass(node.element, "selected");
        });
        
        if (evt && tree.options.onselect) {
            tree.options.onselect(evt, this);
        }

        MochiKit.Signal.signal(self.tree, 'onNodeSelect', evt, this);
    },
    
    onButtonClick : function() {
        if (this.tree.options.onbuttonclick) {
            var evt = arguments[0] || window.event;
            this.tree.options.onbuttonclick(new MochiKit.Signal.Event(evt.target || evt.srcElement, evt), this);
        }      
    },

    getAllChildren : function() {
        
        var result = [];
        
        forEach(this.childNodes, function(n){
            result = result.concat(n);
            result = result.concat(n.getAllChildren());
        });
        
        return result;
    },
    
    toggle : function() {
        
        if (this._ajax_counter)
            return false;

        if (this.expanded) {
            
            this.collapse();
        } else {
            
            this.expand();
        }

        return true;
    },
    
    _loadChildNodes : function(/* optional */expandall) {
        
        if (this._ajax_counter > 0) 
          return;
        
        var self = this;
        
        function _makeChildNodes(records) {
            
            MochiKit.Iter.forEach(records, function(record){
                self.appendChild(self.tree.createNode(record));
            });
            
            if (!expandall) return;
            
            forEach(self.childNodes, function(child){
                child.expand(expandall);
            });
        }
        
        if (!this.record.children) {
            return;
        }
        
        if (this.record.children.length > 0 && !this.record.children[0].id) {
            
            var params = {};
            MochiKit.Base.update(params, this.tree.ajax_params || {});
            MochiKit.Base.update(params, this.record.params || {});
            
            params['ids'] = this.record.children.join(',')

            var req = Ajax.JSON.post(this.tree.ajax_url, params);
            self.tree._ajax_counter += 1;
           
            this.setState('loading');
           
            req.addCallback(function(obj){
                _makeChildNodes(obj.records);
                MochiKit.Signal.signal(self.tree, 'onDataLoad', self.tree, self);
                MochiKit.Signal.signal(self.tree, 'onNodeExpand', self.tree, self);
            });
           
            req.addBoth(function(obj){
                self.tree._ajax_counter -= 1;
                self.setState('collapse');
            });
           
        } else {
            _makeChildNodes(this.record.children);
            MochiKit.Signal.signal(this.tree, 'onNodeExpand', this.tree, this);
        }
        
    },
    
    expand : function(/* optional */all) {
        
        if (!this.hasChildren) {
            return;
        }
        
        all = all || false;
        
        this.setState('collapse');
        this.expanded = true;
        
        if (this.childNodes.length == 0) {
            return this._loadChildNodes(all);    
        }
        
        forEach(this.childNodes, function(node) {
            
            node.element.style.display = "";
            
            if (all) {
                node.expand(all);
            }
        });

        MochiKit.Signal.signal(this.tree, 'onNodeExpand', this.tree, this);
    },
    
    collapse : function() {
        
        if (!this.hasChildren) {
            return;
        }

        forEach(this.childNodes, function(node) {
            node.element.style.display = "none";
            node.collapse();
        });
        
        this.setState('expand');
        this.expanded = false;

        MochiKit.Signal.signal(this.tree, 'onNodeCollapse', this.tree, this);
    },
    
    setState : function(state/* can be 'expand', 'collapse', 'loading' */) {
        
        if (!(this.hasChildren && this.element)) {
            return;
        }

        var span = this.element.getElementsByTagName('span'); span = span[span.length-1];
        MochiKit.DOM.setNodeAttribute(span, 'class', state);
    },
    
    getPath : function() {
        
        // check for dummyNode
        if (!this.record.items) {
            return [];
        }
        
        var path = this.parentNode ? this.parentNode.getPath() : [];
        path.push(this);
        
        return path;
    },
    
    appendChild : function(newChild) {
        return this.insertBefore(newChild);
    },
    
    insertBefore : function(newChild, refChild) {
        
        if (!this.expanded && this.hasChildren && this.childNodes.length == 0) {
            throw ('Child Nodes are not loaded yet.');
        }

        // calculate the row index
        var table = this.tree.table;
        var index = -1;
        
        var n = refChild || this.nextSibling;
        var p = this.parentNode;
        
        while(!n && p) {
            n = p.nextSibling;
            p = p.parentNode;
        }
        
        index = n ? MochiKit.Base.findIdentical(table.rows, n.element) : -1;

        var prev = refChild ? refChild.previousSibling : this.lastChild;
        var next = refChild;
        
        if (prev) { 
            prev.nextSibling = newChild;
        }
        
        if (next) {
            next.previousSibling = newChild;
        }
        
        newChild.parentNode = this;
        newChild.nextSibling = next;
        newChild.previousSibling = prev;
        
        if (next) {
           this.childNodes.splice(MochiKit.Base.findIdentical(this.childNodes, next), 0, newChild);
        } else {
           this.childNodes = this.childNodes.concat(newChild);
        }
        
        this.firstChild = this.childNodes[0];
        this.lastChild = this.childNodes[this.childNodes.length-1];
        
        var row = table.insertRow(index);
        
        var idx = index == -1 ? -1 : index + 1;
        
        // ie6 hack
        table.insertRow(idx);
        
        row = MochiKit.DOM.swapDOM(row, newChild.createDOM());
        
        // ie6 hack
        table.deleteRow(idx);
        
        if (!this.hasChildren) {
            this.hasChildren = true;
            this.element_b.className = 'expand';
        }
        
        return newChild;
    },
    
    removeChild : function(refChild) {
        refChild.__delete__();
    }
}

// vim: sts=4 st=4 et

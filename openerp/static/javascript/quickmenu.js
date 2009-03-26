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

var QuickMenu = function(params) {
	this.__init__(params);
}

QuickMenu.prototype = {
	
	__init__ : function(params){
        this.params = MochiKit.Base.update({
            title: null,        // title
        }, params);
		
		this.layer = $('quick_layer');
		this.box = $('quick_menu');
		this.header = elementDimensions('header');
		
		if (!this.layer) {
            this.layer = DIV({id: 'quick_layer', 
            					style: "z-index: 1; " +
            							"position: absolute; " +
            							"background: gray; " +
            							"top: 0; " +
            							"display: block"});
            							
            appendChildNodes(document.body, this.layer);
            setOpacity(this.layer, 0.4);
            connect(this.layer, 'onclick', this, 'hide');
        }

        if (!this.box) {
        	this.box = document.createElement("iframe");
        	this.box.style.position = 'absolute';
        	this.box.style.top = (this.header.h - 4)  + 'px';
        	this.box.style.display = 'none';
        	this.box.style.zIndex = 2;
        	this.box.style.background = '#FFFFFF';
        	
        	this.box.id = 'quick_menu';
        	this.box.scrolling = 'no';
        	this.box.src = '/quickmenu';
        	this.box.frameborder = 1;
        	
            appendChildNodes(document.body, this.box);
        }
		
	},
	
	show : function(evt) {
		
		setElementDimensions(this.layer, elementDimensions(document.body));
		
        var w = document.body.clientWidth;
        var h = document.body.clientHeight;
		w = w - 2;
        MochiKit.DOM.setElementDimensions(this.box, {w: w, h: h});
		
        var vdh = window.innerHeight || window.screen.availHeight;
//        var vdw = window.innerWidth || window.screen.availWidth;
//     
//        var x = (vdw / 2) - (w / 2);
//        var y = (vdh / 2) - (h / 2);
//        
//        x = Math.max(0, x);
//        y = Math.max(0, y);
//        
//        y = y + document.documentElement.scrollTop;
//        setElementPosition(this.box, {x: x, y: y});

        showElement(this.layer);
        showElement(this.box);

        MochiKit.Signal.signal(this, "show", this);
		
	},
	
	hide : function(evt) {
		hideElement(this.box);
        hideElement(this.layer);
	}
}
	
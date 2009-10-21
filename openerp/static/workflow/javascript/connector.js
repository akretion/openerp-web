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

if (typeof(openerp) == "undefined") {
    openerp = new Object;
}

if (typeof(openerp.workflow) == "undefined") {
    openerp.workflow = new Object;
}


openerp.workflow.Connector=function(id, signal, condition, from, to) {
	
	draw2d.Connection.call(this);
	this.setLineWidth(2);
	this.setColor(new draw2d.Color(180, 180, 180));
	this.setTargetDecorator(new openerp.workflow.ConnectionDecorator());
    
	this.setSourceAnchor(new openerp.workflow.ConnectionAnchor());
    this.setTargetAnchor(new openerp.workflow.ConnectionAnchor());
    this.setRouter(new draw2d.NullConnectionRouter());
	  
	var html = this.getHTMLElement();
	html.style.cursor = 'pointer';
	
	MochiKit.Signal.connect(html, 'ondblclick', this, this.ondblClick);
	MochiKit.Signal.connect(html, 'onmouseover', this, this.onmouseOver);
	MochiKit.Signal.connect(html, 'onmouseout', this, this.onmouseOut);
	MochiKit.Signal.connect(html, 'onclick', this, this.onClick);
	
	
	this.sourceId = null;
	this.destId = null;
	this.setDeleteable(false);
	
	if(id) {
		this.tr_id = id;
		this.signal = signal;
		this.condition = condition;
		this.from = from;
		this.to = to;
		this.isOverlaping = false;
		this.OverlapingSeq = 0;
		this.totalOverlaped = 0;
		
		this.sourceAnchor.conn_id = id;
		this.targetAnchor.conn_id = id;
	}
}

openerp.workflow.Connector.prototype = new draw2d.Connection();

openerp.workflow.Connector.prototype.ondblClick = function(event) {	
		new InfoBox(this).show(event);
}

openerp.workflow.Connector.prototype.onClick = function(event) {
    
    if (WORKFLOW.selected==this)
        new InfoBox(this).show(event);
}


openerp.workflow.Connector.prototype.onmouseOver = function(event) {
    getElement('status').innerHTML = "Condition: " + this.condition + " | Signal: "+ this.signal;
}


openerp.workflow.Connector.prototype.onmouseOut = function(event){
    getElement('status').innerHTML = '';
}

openerp.workflow.Connector.prototype.edit = function() {
	
	params = {
	'_terp_model' : 'workflow.transition',
	'_terp_start' : this.getSource().getParent().get_act_id(),
	'_terp_end' : this.getTarget().getParent().get_act_id()
	}
	
	if(!isUndefinedOrNull(this.tr_id))
		params['_terp_id'] = this.tr_id;	
		
	var act = openobject.http.getURL('/workflow/connector/edit', params);
	openobject.tools.openWindow(act);
}

openerp.workflow.Connector.prototype.get_tr_id = function() {
	return this.tr_id;
}

openerp.workflow.Connector.prototype.__delete__ = function() {
		MochiKit.Signal.disconnectAll(this.getHTMLElement(), 'ondblclick', 'onmouseover', 'onmouseout', 'onclick');
}

openerp.workflow.Connector.prototype.setSource = function(port) {
	
	draw2d.Connection.prototype.setSource.call(this,port);
	
	if(this.sourceId==null)
		this.sourceId = port.getParent().get_act_id();
	else if(this.sourceId != port.getParent().get_act_id())	{
		this.sourceId = port.getParent().get_act_id();
		req = openobject.http.postJSON('/workflow/connector/change_ends', {id: this.tr_id, field: 'act_from', value: this.sourceId});
	}
}

openerp.workflow.Connector.prototype.setTarget = function(port) {
	draw2d.Connection.prototype.setTarget.call(this,port);
	
	if(this.destId==null)
		this.destId = port.getParent().get_act_id();
	else if(this.destId != port.getParent().get_act_id()) {
		this.destId = port.getParent().get_act_id();
		req = openobject.http.postJSON('/workflow/connector/change_ends', {id: this.tr_id, field: 'act_to', value: this.destId});
	}
}

// vim: ts=4 sts=4 sw=4 si et



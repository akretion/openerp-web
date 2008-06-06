
// requires: mootools & draw2d

if (typeof(openerp) == "undefined") {
    openerp = new Object;
}

if (typeof(openerp.workflow) == "undefined") {
    openerp.workflow = new Object;
}



openerp.workflow.Workflow = new Class;
openerp.workflow.Workflow.prototype = $merge(openerp.workflow.Workflow.prototype, draw2d.Workflow.prototype);

openerp.workflow.Workflow.implement({
	
	initialize : function(canvas) {
		
		draw2d.Workflow.call(this,canvas);
		this.getCommandStack().setUndoLimit(0);
		
		this.states = new draw2d.ArrayList();
		this.conn = new draw2d.ArrayList();
		this.id = null;
		
		//this.setToolWindow(toolbar, 30, 30);
		var tbar = new openerp.workflow.Toolbar();
		this.toolPalette = tbar;
		tbar.setWorkflow(this);
		tbar.canDrag = false;
		
		tbar = tbar.getHTMLElement();
		tbar.style.position = 'relative';
		tbar.style.top = '0px';
		tbar.style.left = '0px';
		
        MochiKit.DOM.appendChildNodes('toolbox', tbar);
		
//		dummy state
		this.state = new openerp.workflow.State();
        this.state.setDimension(100, 60);
		this.state.setBackgroundColor(new draw2d.Color(255, 255, 255));
        this.addFigure(this.state, 100, 20);
		this.state.initPort();
		var html_state = this.state.getHTMLElement();	
		html_state.style.display = 'none';
		
		var state_ports = this.state.getPorts();
		
		//dummy connector
		this.connector = new openerp.workflow.Connector(999);
		this.connector.setSource(state_ports.get(0));
		this.connector.setTarget(state_ports.get(3));			
		this.addFigure(this.connector);
		var html_conn = this.connector.getHTMLElement();
		html_conn.style.display = 'none';
		
		this.draw_graph(getElement('wkf_id').value);
	},
	
	draw_graph : function(wkf_id) {
		
		this.id = wkf_id;
		self = this;
		
		for(i=0; i<this.conn.getSize(); i++) {
			this.conn.get(i).dispose();
			MochiKit.DOM.removeElement(this.conn.get(i).getHTMLElement());
		}
		
		var figures = this.getFigures();
		var n = figures.getSize();		
		var arr = [];
				
		for(var i=0; i<n; i++) {
						
			var fig = figures.get(i);
			if (fig instanceof openerp.workflow.State) {
				arr.push(fig);
			}
		}
		
		for(var i=0; i<arr.length; i++) {
			this.removeFigure(arr[i]);
		}
		
		this.states.removeAllElements();
		this.conn.removeAllElements();
		
		req = Ajax.JSON.post('/workflow/get_wkfl_info',{id:wkf_id});
		req.addCallback(function(obj) {	
			
			for(i in obj.list) {
				
				var node = obj.list[i];
				var s = new openerp.workflow.State(node['id'], node['name'], node['flow_start'], node['flow_stop']);	
		        self.addFigure(s, node['y']+100, node['x']);
		        s.initPort();
		        self.states.add(s);
			}
			 
			var n = self.states.getSize();
			
			for(i in obj.conn) {
				
				var conn = obj.conn[i];
				var start = 0;
				var end = 0;
				
				for(j=0; j<n; j++) {
						
					var node = self.states.get(j);
					var id = node.act_id;
					
					if(id==conn['c'][0])
						start = j;							
					else if(id==conn['c'][1])
						end =j;
				}
				self.add_conn(conn['id'], start, end, conn['signal'],conn['condition']);
			}
			
	    	getElement('loading').style.display = 'none';
		});	
		
	},
	
	add_conn : function(id, start, end, signal, condition) {
		
		var source = this.states.get(start);
		var destination = this.states.get(end);		
		
		var source_ports = source.getPorts();
		var dest_ports = destination.getPorts();
		
		var c = new openerp.workflow.Connector(id, signal, condition);	
		var n1 = source_ports.getSize();
		var n2 = dest_ports.getSize();
		
		if(source.getPosition().x<destination.getPosition().x) {
			
			for(i=0; i<n1; i++) {
				if(source_ports.get(i).getFanOut()>0)
					continue;
				else
				{
					c.setSource(source_ports.get(i));
					break;
				}	
			}
			
			for(i=n2-1; i>=0; i--) {
				if(dest_ports.get(i).getFanOut()>0)
					continue;
				else
				{
					c.setTarget(dest_ports.get(i));
					break;
				}	
			}				
		} else {	
					
			for(i=n1-1; i>=0; i--) {
				if(source_ports.get(i).getFanOut()>0)
					continue;
				else
				{
					c.setSource(source_ports.get(i));
					break;
				}	
			}
			
			for(i=0; i<n2; i++)	{
				if(dest_ports.get(i).getFanOut()>0)
					continue;
				else
				{
					c.setTarget(dest_ports.get(i));
					break;
				}	
			}
		}
		
		self.addFigure(c);
		this.conn.add(c);
	},
	
	create_state : function(id) {
		log('id:'+id);
		if(id != 0) {	
				
			var position = this.state.getPosition();	
			self = this;
			
			req = Ajax.JSON.post('/workflow/state/get_info',{id:id});
			req.addCallback(function(obj) {
				var flag = false;
				var index = null;
				var n = self.states.getSize(); 
				
				for(i=0; i<n; i++) {
					if(self.states.get(i).get_act_id()==id)
					{
						flag=true;
						index = i;
						break;
					}
				}				
				
				if(!flag) {	
					var s = new openerp.workflow.State(obj.data['id'],obj.data['name'],obj.data['flow_start'],obj.data['flow_stop']);
			        self.addFigure(s, position.x, position.y);
			        self.states.add(s);
			        s.initPort();
				} else {
					var state = self.states.get(index);
					var span = MochiKit.DOM.getElementsByTagAndClassName('span',null,state.getHTMLElement());
					log(span[0],obj.data['name']);
					span[0].innerHTML = obj.data['name'];
//					div.style.width = Math.max(50,(obj.data['name'].length/2*10))+'px'							
					
//					if(obj.data['flow_start'] || obj.data['flow_stop'] )
//					{	
//						state.setBackgroundColor(new draw2d.Color(155, 155, 155));
//						log('if')
//					}
//					else
//					{
//						state.setBackgroundColor(new draw2d.Color(255, 255, 255));
//						log('else');
//					}
				}	
			});
		} else {
			alert('state could not be created');
		}
	},
	
	create_conn : function(act_from, act_to){
		
		var self = this;
		var html = this.connector.getHTMLElement();
		
		req = Ajax.JSON.post('/workflow/connector/save_tr', {act_from:act_from, act_to:act_to});
		req.addCallback(function(obj) {	
			
			html.style.display = 'none';
			
			if(obj.flag) {
				var n = self.states.getSize();
				var start = 0;
				var end = 0;
				
				for(j=0; j<n; j++) {	
					var node = self.states.get(j);
					var id = node.get_act_id();
					if(id==act_from)
						start = j;							
					else if(id==act_to)
						end =j;
				}
				
				self.add_conn(obj.data['id'],start,end,obj.data['signal'],obj.data['condition']);
				self.conn.getLastElement().edit();
			} else {
				alert('could not create transaction at server');
			}
		});		
	},
	
	
	update_conn : function(id) {		
		log('in update_conn :'+id);
		var self = this;
		
		req = Ajax.JSON.post('/workflow/connector/get_info',{id:id});
		req.addCallback(function(obj) {
			log(obj.data['act_from'][0],obj.data['act_to'][0]);
			var n = self.conn.getSize();
			
			for(i=0; i<n; i++) {
				var c = self.conn.get(i);
				log(c.get_tr_id());
				if(id==c.get_tr_id()) {
					c.signal = obj.data['signal'];
					c.condition = obj.data['condition'];
					break;		
				}
			}			
		});
	},
	
	remove_elem : function(elem) {

	if(elem instanceof openerp.workflow.State)
		this.unlink_state(elem);
	else if(elem instanceof openerp.workflow.Connector)
		this.unlink_connector(elem);
		
	},
	
	unlink_state : function(state) {
		
		params = {
		'model' : 'workflow.activity',
		'id' : state.get_act_id()		
		}
		
		var self = this;
		
		req = Ajax.JSON.post('/workflow/state/delete',params);
		req.addCallback(function(obj) {
			
			if(!obj.error) {
				state.__delete__();
				self.remove_state(state);
			} else {
				alert(obj.error);
			}			
		});
	},
	
	remove_state : function(state) {
		
		var command = new draw2d.CommandDelete(self.getFigure(state.getId()));
		self.getCommandStack().execute(command);
		self.states.remove(state);
	},
	
	
	unlink_connector : function(conn) {
		
		var self = this;
		params = {
		'model' : 'workflow.transition',
		'id' : conn.get_tr_id()		
		}
		
		req = Ajax.JSON.post('/workflow/connector/delete',params);
		req.addCallback(function(obj) {
			
			if(!obj.error) {				
				conn.__delete__();
				self.remove_conn(conn);
			} else
				alert(obj.error);
			
		});
	},
	
	remove_conn : function(conn) {
		conn.dispose();
		this.conn.remove(conn);
	}
});
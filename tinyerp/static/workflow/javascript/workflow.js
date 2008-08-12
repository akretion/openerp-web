
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
		
		draw2d.Workflow.call(this, canvas);
		this.setBackgroundImage(null, false);
		this.getCommandStack().setUndoLimit(0);
		
		this.states = new draw2d.ArrayList();
		this.connectors = new draw2d.ArrayList();
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
		tbar.style.zIndex = 0;
		
        MochiKit.DOM.appendChildNodes('toolbox', tbar);
		
//		dummy state
		this.state = new openerp.workflow.StateOval({});
        this.state.setDimension(100, 60);
		this.state.setBackgroundColor(new draw2d.Color(255, 255, 255));
        this.addFigure(this.state, 100, 20);
		this.state.initPort();
		this.state.initPort();
		this.state.getHTMLElement().style.display = 'none';	
		
		this.draw_graph(getElement('wkf_id').value);
	},
	
	draw_graph : function(wkf_id) {
		
		this.id = wkf_id;
		var self = this;
		
		req = Ajax.JSON.post('/workflow/get_info',{id:wkf_id});
		req.addCallback(function(obj) {	
			
			for(i in obj.nodes) {
			    var node = obj.nodes[i];
	
		        if(!node['subflow_id'])
		          var state = new openerp.workflow.StateOval(node);
		        else
		          var state = new openerp.workflow.StateRectangle(node);
		          
		        self.addFigure(state, node['y'], node['x']);
		        state.initPort();
		        self.states.add(state);
			}
			
			//check for overlapping connections
			for(i in obj.conn) {
				var counter = 1;
				var check_for = obj.conn[i];
				check_for['isOverlaping'] = false;
				
				for(k in obj.conn) {
					if(i!=k) {
						check_to = obj.conn[k];
						
						if(check_for['s_id']==check_to['s_id'] && check_for['d_id']==check_to['d_id']) {
							check_for['isOverlaping'] = true;
							counter++;
						}
						else if(check_for['d_id']==check_to['s_id'] && check_for['s_id']==check_to['d_id']) {
							check_for['isOverlaping'] = true;
							counter++;
						}						
					}
					else {
						check_for['OverlapingSeq'] = counter;
					}
				}
				check_for['totalOverlaped'] = counter;
			}			
			 
			var n = self.states.getSize();
			
			for(i in obj.conn) {				
				var conn = obj.conn[i];
				var start = 0;
				var end = 0;
				
				for(j=0; j<n; j++) {
						
					var node = self.states.get(j);
					var id = node.act_id;
					
					if(id==conn['s_id'])
						start = j;							
					else if(id==conn['d_id'])
						end =j;
				}
                self.add_connection(start, end, conn)
			}
			
	    	getElement('loading').style.display = 'none';
		});	
	
		
	},
	
	get_overlaping_connection : function(s, e, flag) {
		
		var n = this.connectors.getSize();
		var conn_overlapped = new Array();
		var counter = 1;
		
		for(i=0; i<n; i++) {
			var conn = this.connectors.get(i)
			var start = conn.getSource().getParent().get_act_id();
			var end = conn.getTarget().getParent().get_act_id();
			
			if((start==s && end==e)) {
				conn.isOverlaping = true;
				conn.OverlapingSeq = counter ++;
				conn_overlapped.push(i);
			}else if(end==s && start==e) {
				conn.isOverlaping = true;
				conn.OverlapingSeq = counter ++;
				conn_overlapped.push(i);	
			}
		}
		
		for(i=0; i<conn_overlapped.length; i++) {
			var conn = this.connectors.get(conn_overlapped[i]) 
			
			if(flag) {
				conn.totalOverlaped = counter;
			} else {
				conn.totalOverlaped = counter - 1;
				if(counter-1==1)
					conn.isOverlaping = false;
			}
		}
		
		return counter;
	},	
	
	add_connection : function(start, end, params) {
        
        var source = this.states.get(start);
        var destination = this.states.get(end);     
               
        var conn = new openerp.workflow.Connector(params.id, params.signal, params.condition, params.source, params.destination); 
        var n = this.connectors.getSize();
        
        //self connection
        if(start==end) {
            conn.setSourceAnchor(new draw2d.ConnectionAnchor);
            conn.setTargetAnchor(new draw2d.ConnectionAnchor);
            conn.setRouter(new draw2d.BezierConnectionRouter());        
        }
        
        conn.isOverlaping = params.isOverlaping;       
        conn.OverlapingSeq = params.OverlapingSeq;
        conn.totalOverlaped = params.totalOverlaped;
        
        var spos = source.getBounds();
        var dpos = destination.getBounds();
    
        //fix source and destination ports 
        if(spos.x<dpos.x) {
            conn.setTarget(destination.portL);
            
            if((spos.y + spos.h - dpos.y)>50) 
                conn.setSource(source.portD);
            else if((dpos.y + dpos.h - spos.y)>50)
                conn.setSource(source.portU);
            else 
                conn.setSource(source.portR);
        }
        else {
            conn.setTarget(destination.portR);
            
            if((spos.y + spos.h - dpos.y)>50) 
                conn.setSource(source.portD);
            else if((dpos.y + dpos.h - spos.y)>50)
                conn.setSource(source.portU);
            else
                conn.setSource(source.portL);
        }
        
        this.addFigure(conn);
        this.connectors.add(conn);
    },
	
	create_state : function(id) {
	    
		if(id != 0) {	
			var position = this.state.getPosition();	
			var self = this;
			
			req = Ajax.JSON.post('/workflow/state/get_info',{id: id});
			req.addCallback(function(obj) {
				var flag = false;
				var index = null;
				var n = self.states.getSize(); 
				var data = obj.data;
				
				for(i=0; i<n; i++) {
					if(self.states.get(i).get_act_id() == id)
					{
						flag=true;
						index = i;
						break;
					}
				}			
				
				if(!flag) {	
				    
			        if(!data['subflow_id'])
			             var state = new openerp.workflow.StateOval(data);
			        else
			             var state = new openerp.workflow.StateRectangle(data);
			             
			        self.addFigure(state, position.x, position.y);
			        self.states.add(state);
			        state.initPort();
				} else {
					var state = self.states.get(index);
					var span = getElement(state.sname);
					span.innerHTML = data['name'];
					span.id = data['name'];
					
					state.action = data['action'];
					state.kind = data['kind'];
                    state.sname = data['name'];
					
//					if(data['flow_start'] || data['flow_stop'])
//						state.setBackgroundColor(new draw2d.Color(155, 155, 155));
//					else
//						state.setBackgroundColor(new draw2d.Color(255, 255, 255));
				}	
			});
		} else {
			alert('state could not be created');
		}
	},
	
	create_connection : function(act_from, act_to) {
		
		var self = this;
		
		req = Ajax.JSON.post('/workflow/connector/auto_create', {act_from: act_from, act_to: act_to});
		req.addCallback(function(obj) {	
			
			var data = obj.data;
			
			if(obj.flag) {
				var n = self.states.getSize();
				var start = 0;
				var end = 0;
				
				for(j=0; j<n; j++) {	
					var node = self.states.get(j);
					var id = node.get_act_id();
					if(id==act_from)
						start = j;							
					if(id==act_to)
						end = j;
				}
				
				var counter = self.get_overlaping_connection(data['act_from'][0], data['act_to'][0], 1)
				
				var params = {
				    id: data['id'],
				    signal: data['signal'],
				    condition: data['condition'],
				    source: data['act_from'][1],
				    destination: data['act_to'][1]
				};
				
				if(counter>1) {
					params['isOverlaping'] = true;
					params['OverlapingSeq'] = counter;
					params['totalOverlaped'] = counter;
				}		
				
				self.add_connection(start, end, params);
				self.connectors.getLastElement().edit();
			} else {
				alert('Could not create transaction at server');
			}
		});		
	},
	
	
	update_connection : function(id) {	
		var self = this;
		
		req = Ajax.JSON.post('/workflow/connector/get_info',{id: id});
		req.addCallback(function(obj) {
			var n = self.connectors.getSize();
			
			for(i=0; i<n; i++) {
				var conn = self.connectors.get(i);
				if(id==conn.get_tr_id()) {
					conn.signal = obj.data['signal'];
					conn.condition = obj.data['condition'];
					break;		
				}
			}			
		});
	},
	
	
	remove_elem : function(elem) {

	if(elem instanceof openerp.workflow.StateOval || elem instanceof openerp.workflow.StateRectangle)
		this.unlink_state(elem);
	else if(elem instanceof openerp.workflow.Connector)
		this.unlink_connector(elem);
	},
	
	
	unlink_state : function(state) {
		
		var self = this;
		
		req = Ajax.JSON.post('/workflow/state/delete', {'id' : state.get_act_id()});
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
		
		var command = new draw2d.CommandDelete(this.getFigure(state.getId()));
		this.getCommandStack().execute(command);
		this.states.remove(state);
	},
	
	
	unlink_connector : function(conn) {
		
		var self = this;
		
		req = Ajax.JSON.post('/workflow/connector/delete', {'id' : conn.get_tr_id()});
		req.addCallback(function(obj) {
			
			if(!obj.error) {				
				conn.__delete__();
				self.remove_conn(conn);
			} else
				alert(obj.error);
			
		});
	},
	
	
	remove_conn : function(conn) {
		var start = conn.getSource().getParent().get_act_id();
		var end = conn.getTarget().getParent().get_act_id();
		
		this.connectors.remove(conn);		
		if(conn.isOverlaping)	
			this.get_overlaping_connection(start, end, 0);
			
		this.removeFigure(conn);
	}
});

var InfoBox = function(source) {
    this.__init__(source);
}

InfoBox.prototype = {
	
	__init__ : function(source){		
		
		this.source = source;		
		this.layer = $('calInfoLayer');
        this.box = $('calInfoBox');

        var btnCancel = BUTTON({'class': 'button', 'type': 'button'}, 'Cancel');
        var btnEdit = BUTTON({'class': 'button', 'type': 'button'}, 'Edit');  
        var btnDelete = BUTTON({'class': 'button', 'type': 'button'}, 'Delete');
        
        MochiKit.Signal.connect(btnCancel, 'onclick', this, 'hide');
        MochiKit.Signal.connect(btnEdit, 'onclick', this, 'onEdit'); 
        MochiKit.Signal.connect(btnDelete, 'onclick', this, 'onDelete');
        
        var title = 'Information Box';
        
        if(this.source instanceof openerp.workflow.StateOval || this.source instanceof openerp.workflow.StateRectangle) {
       	  	 var id = 'Id: ' + this.source.get_act_id();
       		 var dtl1 = 'Action: ' + this.source.action;
       		 var dtl2 = 'Kind: ' + this.source.kind;
        } else {
        	var id = this.source.from+ ' ---> ' + this.source.to;
        	var dtl1 = 'Signal: ' + this.source.signal;
        	var dtl2 = 'Condition: ' + this.source.condition;
        }
        
        var info = DIV(null,
                    DIV({'class': 'calInfoTitle'}, title),
                    DIV({'class': 'calInfoDesc'}, id),
                    DIV({'class': 'calInfoDesc'}, dtl1),
                    DIV({'class': 'calInfoDesc'}, dtl2),
                        TABLE({'class': 'calInfoButtons', 'cellpadding': 2}, 
                            TBODY(null, 
                                TR(null,
                                    TD(null, btnEdit),                                   
                                    TD(null, btnDelete),
                                    TD({'align': 'right', 'width': '100%'}, btnCancel)))));
                                    
                                    
         if (!this.layer) {
            this.layer = DIV({id: 'calInfoLayer'});
            MochiKit.DOM.appendChildNodes(document.body, this.layer);
            setOpacity(this.layer, 0.3);
            connect(this.layer, 'onclick', this, 'hide');
        }
        
         if (!this.box) {
            this.box = DIV({id: 'calInfoBox'});
            MochiKit.DOM.appendChildNodes(document.body, this.box);
        }
        
        this.box.innerHTML = "";        
        MochiKit.DOM.appendChildNodes(this.box, info);
	},	
	
	show : function(evt) {
		
        MochiKit.DOM.setElementDimensions(this.layer, elementDimensions(document.body));
        //setElementDimensions(this.layer, getViewportDimensions());

        var w = 350;
        var h = 125;

        MochiKit.DOM.setElementDimensions(this.box, {w: w, h: h});

        var x = evt.mouse().page.x;
        var y = evt.mouse().page.y;

        x -= w / 2;
        y -= h - h / 3;

        var vd = elementDimensions(document.body);
        var md = elementDimensions(this.box);

        if ((x + md.w) > vd.w) {
            x -= x + md.w - vd.w;
        }

        x = Math.max(0, x);
        y = Math.max(0, y);

        MochiKit.DOM.setElementPosition(this.box, {x: x, y: y});

        MochiKit.DOM.showElement(this.layer);
        MochiKit.DOM.showElement(this.box);
    },	
	
    hide : function(evt) {
        MochiKit.DOM.hideElement(this.box);
        MochiKit.DOM.hideElement(this.layer);
    },
    
    onEdit : function(){
        this.hide();
        this.source.edit();
    },
      
    onDelete : function(){
    	
		this.hide();
        if (!confirm('Do you realy want to delete this record?')) {
            return false;
        }
		WORKFLOW.remove_elem(this.source);
    }
}


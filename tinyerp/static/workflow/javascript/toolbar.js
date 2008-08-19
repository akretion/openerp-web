
// requires: mootools & draw2d

if (typeof(openerp) == "undefined") {
    openerp = new Object;
}

if (typeof(openerp.workflow) == "undefined") {
    openerp.workflow = new Object;
}

// Toolbar Class
openerp.workflow.Toolbar = new Class;
openerp.workflow.Toolbar.prototype = $merge(openerp.workflow.Toolbar.prototype, draw2d.ToolPalette.prototype);

openerp.workflow.Toolbar.implement({
    
    initialize : function() {

        draw2d.ToolPalette.call(this, "Tools");

        this.tool1 = new openerp.workflow.ToolShowGrid(this);
        this.tool2 = new openerp.workflow.ToolCreateState(this);
			
        this.tool1.setPosition(13, 10);
        this.tool2.setPosition(13, 40);
        
        this.addChild(this.tool1);
        this.addChild(this.tool2);

        this.setDimension(30, 300);
    },
    
    createHTMLElement : function() {

        var item = draw2d.ToolPalette.prototype.createHTMLElement.call(this);

        item.style.backgroundImage = 'none';//"url(/static/workflow/images/window_bg.png)";

        if (this.hasTitleBar()) {
            this.titlebar.style.backgroundImage = "url(/static/workflow/images/window_toolbar.png)";
        }

        
        return item;
    },

    onSetDocumentDirty : function() {
    }

});

// Tool buttons

// Class: ToolToggle
openerp.workflow.ToolToggle = new Class;
openerp.workflow.ToolToggle.prototype = $merge(openerp.workflow.ToolToggle.prototype, draw2d.ToggleButton.prototype);

openerp.workflow.ToolToggle.implement({
    
    initialize : function(palette, image) {
        this.image = image;        
        draw2d.ToggleButton.call(this, palette);
        this.getHTMLElement().title = 'Show grid';
    },

    getImageUrl : function() {
        return this.image;
    }
});

// Class: ToolGeneric
openerp.workflow.ToolGeneric = new Class;
openerp.workflow.ToolGeneric.prototype = $merge(openerp.workflow.ToolGeneric.prototype, draw2d.ToolGeneric.prototype);

openerp.workflow.ToolGeneric.implement({
    
    initialize : function(palette, image) {
        this.image = image;
        draw2d.ToolGeneric.call(this, palette);
        this.getHTMLElement().title = 'Create State';
    },

    getImageUrl : function() {
        return this.image;
    }
});

// Class: ToolShowGrid
openerp.workflow.ToolShowGrid = openerp.workflow.ToolToggle.extend({

    initialize : function(palette) {
        this.parent(palette, '/static/workflow/images/ToolShowGrid.jpg');
    },

    execute : function() {
        var isdown = this.isDown();
        
        WORKFLOW.setBackgroundImage(isdown ? '/static/workflow/images/grid_10.jpg' : null, isdown);
        WORKFLOW.setGridWidth(10, 10);
        WORKFLOW.setSnapToGrid(isdown);
    }
});

// Class: ToolCreateState
openerp.workflow.ToolCreateState = openerp.workflow.ToolGeneric.extend({

    initialize : function(palette) {
        this.parent(palette, '/static/workflow/images/ToolOval.jpg');
    },

	execute : function(x, y) {
	    
		WORKFLOW.state.setPosition(x,y);
		
		var html = WORKFLOW.state.getHTMLElement();
		html.style.display = '';
		WORKFLOW.state.edit();
		html.style.display = 'none';

        // call the parent method
        openerp.workflow.ToolGeneric.prototype.execute.call(this, x, y);
    }
});



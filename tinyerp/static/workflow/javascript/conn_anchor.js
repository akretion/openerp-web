
if (typeof(openerp) == "undefined") {
    openerp = new Object;
}

if (typeof(openerp.workflow) == "undefined") {
    openerp.workflow = new Object;
}

openerp.workflow.ConnectionAnchor = new Class;
openerp.workflow.ConnectionAnchor.prototype = $merge(openerp.workflow.ConnectionAnchor.prototype, draw2d.ChopboxConnectionAnchor.prototype);

openerp.workflow.ConnectionAnchor.implement({

	initialize : function(owner) {
		draw2d.ChopboxConnectionAnchor.call(this,owner);
	},
	
	getLocation : function(/*:draw2d.Point*/ reference)
	{
		var r = new draw2d.Dimension();
   		r.setBounds(this.getBox());
   		r.translate(-1, -1);
   		r.resize(1, 1);

		var centerX = r.x + r.w/2;
		var centerY = r.y + r.h/2;
		
		if (r.isEmpty() || (reference.x == centerX && reference.y == centerY))
			return new /*NAMESPACE*/Point(centerX, centerY);  //This avoids divide-by-zero
		
		var dx = reference.x - centerX;
		var dy = reference.y - centerY;
		//r.width, r.height, dx, and dy are guaranteed to be non-zero. 
		var scale = 0.5 / Math.max(Math.abs(dx) / r.w, Math.abs(dy) / r.h);
		
		dx *= scale;
		dy *= scale;
		
		centerX += dx;
		centerY += dy;

		var conn = this.owner.getConnections().get(0);
		this.find_angle(conn);
		return new draw2d.Point(Math.round(centerX)+(conn.OverlapingSeq*10), Math.round(centerY)+(conn.OverlapingSeq*10));
	},
	
	find_angle : function(c) {
		var center1 = c.sourceAnchor.getReferencePoint();
		var center2 = c.targetAnchor.getReferencePoint();
		
//		log('x1:'+center1.x+'y1:'+center1.y);
//		log('x2:'+center2.x+'y2:'+center2.y);
		
		if(center1.x!=center2.x){
			a = 180/3.14 * Math.atan((center2.y-center1.y)/(center2.x-center1.x));
//			log(a);
		}
	}

});
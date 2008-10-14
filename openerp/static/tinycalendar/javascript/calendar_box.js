////////////////////////////////////////////////////////////////////////////////
//
// Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
//
// $Id$
//
// Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
//
// WARNING: This program as such is intended to be used by professional
// programmers who take the whole responsibility of assessing all potential
// consequences resulting from its eventual inadequacies and bugs
// End users who are looking for a ready-to-use solution with commercial
// guarantees and support are strongly advised to contract a Free Software
// Service Company
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.
//
////////////////////////////////////////////////////////////////////////////////

var InfoBox = function(params) {
    this.__init__(params);
}

InfoBox.prototype = {

    __init__ : function(params){
        this.params = MochiKit.Base.update({
            dtStart : null,     // start time
            dtEnd : null,       // end time
            nRecordID : null,   // record id
            title: null,        // title
            description: null   // description
        }, params);

        this.layer = $('calInfoLayer');
        this.box = $('calInfoBox');

        var btnCancel = BUTTON({'class': 'button', 'type': 'button'}, 'Cancel');
        var btnEdit = BUTTON({'class': 'button', 'type': 'button'}, 'Edit');
        var btnCopy = BUTTON({'class': 'button', 'type': 'button'}, 'Duplicate');
        var btnDelete = BUTTON({'class': 'button', 'type': 'button'}, 'Delete');

        MochiKit.Signal.connect(btnCancel, 'onclick', this, 'hide');
        MochiKit.Signal.connect(btnEdit, 'onclick', this, 'onEdit');
        MochiKit.Signal.connect(btnCopy, 'onclick', this, 'onCopy');
        MochiKit.Signal.connect(btnDelete, 'onclick', this, 'onDelete');
        
        var DT_FORMAT = getElement('calMonth') ? getNodeAttribute('calMonth', 'dtFormat') : getNodeAttribute('calWeek', 'dtFormat');
        var H_FORMAT = '%I:%M %P';
        var DTH_FORMAT = DT_FORMAT + ' ' + H_FORMAT;

        var title = this.params.title;                         
        var desc = '(' + this.params.dtStart.strftime(DTH_FORMAT) + ' - ' + this.params.dtEnd.strftime(DTH_FORMAT) + ')';

        if (this.params.dtStart.strftime(DT_FORMAT) == this.params.dtEnd.strftime(DT_FORMAT)){
            var desc = '(' + this.params.dtStart.strftime(DTH_FORMAT) + ' - ' + this.params.dtEnd.strftime(H_FORMAT) + ')';
        }

        var desc = SPAN(null, this.params.description, BR(), desc);

        var info = DIV(null,
                    DIV({'class': 'calInfoTitle'}, title),
                    DIV({'class': 'calInfoDesc'}, desc),
                        TABLE({'class': 'calInfoButtons', 'cellpadding': 2}, 
                            TBODY(null, 
                                TR(null,
                                    TD(null, btnEdit),
                                    TD(null, btnCopy),
                                    TD(null, btnDelete),
                                    TD({'align': 'right', 'width': '100%'}, btnCancel)))));

        if (!this.layer) {
            this.layer = DIV({id: 'calInfoLayer'});
            appendChildNodes(document.body, this.layer);
            setOpacity(this.layer, 0.3);
            connect(this.layer, 'onclick', this, 'hide');
        }

        if (!this.box) {
            this.box = DIV({id: 'calInfoBox'});
            appendChildNodes(document.body, this.box);
        }

        this.box.innerHTML = "";

        appendChildNodes(this.box, info);
    },

    show : function(evt) {

        setElementDimensions(this.layer, elementDimensions(document.body));
        //setElementDimensions(this.layer, getViewportDimensions());

        var w = 350;
        var h = 125;

        setElementDimensions(this.box, {w: w, h: h});

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

        setElementPosition(this.box, {x: x, y: y});

        showElement(this.layer);
        showElement(this.box);
    },

    hide : function(evt) {
        hideElement(this.box);
        hideElement(this.layer);
    },

    onEdit : function(){
        this.hide();
        editCalendarRecord(this.params.nRecordID);
    },
    
    onCopy : function(){
        this.hide();
        var req = copyCalendarRecord(this.params.nRecordID);
        req.addCallback(function(res){
            getCalendar();
        });
    },

    onDelete : function(){

        this.hide();

        if (!confirm('Do you realy want to delete this record?')) {
            return false;
        }
        
        var req = Ajax.JSON.post('/calendar/delete', {
           _terp_id: this.params.nRecordID,
           _terp_model: getElement('_terp_model').value 
        });
        
        var self = this;
        
        req.addCallback(function(obj){
            
           if (obj.error) {
               return alert(obj.error);
           }
           
           var id = parseInt(getElement('_terp_id').value) || 0;
           var ids = [];
           
           try {
               ids = eval('(' + getElement('_terp_ids').value + ')') || [];
           }catch(e){}
           
           var idx = MochiKit.Base.findIdentical(ids, self.params.nRecordID);
           
           if (id == self.params.nRecordID) {
               getElement('_terp_id').value = 'False';
           }
           
           if (idx > -1) {
               ids = ids.splice(idx, 1);
               getElement('_terp_ids').value = '[' + ids.join(', ') + ']';
           }
           
           getCalendar();
        });
    }
}

// vim: ts=4 sts=4 sw=4 si et


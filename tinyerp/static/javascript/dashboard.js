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
// This program is Free Software; you can redistribute it and/or
// modify it under the terms of the GNU General Public License
// as published by the Free Software Foundation; either version 2
// of the License, or (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program; if not, write to the 
// Free Software Foundation, Inc., 59 Temple Place - Suite 330, 
// Boston, MA  02111-1307, USA.
//
////////////////////////////////////////////////////////////////////////////////

function initialize_dashboard() {

    var dashbars = MochiKit.DOM.getElementsByTagAndClassName('div', 'dashbar');
    MochiKit.Iter.forEach(dashbars, function(bar){
        
        new Droppable(bar, {'ondrop': onDrop, 
                            'hoverclass': 'dashbar-hover',
                            'accept': ['dashlet']});
        
        var dashlets = MochiKit.DOM.getElementsByTagAndClassName('div', 'dashlet', bar);
        MochiKit.Iter.forEach(dashlets, function(dashlet){
            new Draggable(dashlet, {'handle': 'dashlet-title', 
                                    'starteffect': null, 
                                    'endeffect': null, 
                                    'revert': true});
        });        
    });

    function onDrop(src, dst, evt) {

        var xy = MochiKit.DOM.elementPosition(src, dst);
        var ref = null;

        var divs = MochiKit.DOM.getElementsByTagAndClassName('div', 'dashlet', dst);

        for(var i=0; i < divs.length; i++) {

            var el = divs[i];
            var dim = MochiKit.DOM.elementDimensions(el);
            var pos = MochiKit.DOM.elementPosition(el);

            if ((pos.y > xy.y) && (xy.y < (pos.y + dim.h))) {
                ref = el;
                break;
            }
        }
        
        dst.insertBefore(src, ref);

        src.style.position = 'relative';
        src.style.top = 'auto';
        src.style.left = 'auto';
        src.style.width = '100%';

        if (src && ref != src) {
            
            var src_id = src.id.replace('dashlet_', '');
            var ref_id = ref ? ref.id.replace('dashlet_', '') : null;

            var args = {src: src_id, dst: dst.id, ref: ref_id};
            args['view_id'] = getElement('_terp_view_id').value;

            var req = Ajax.JSON.post('/viewed/update_dashboard', args); 
            req.addCallback(function(obj) {

                if (obj.error) {
                    return alert(obj.error);    
                }

                if (obj.reload) {
                    window.location.reload();    
                }
            });
        }
    }

    connect(MochiKit.DragAndDrop.Draggables, 'onStart', function(evt) {
            var embed = getElementsByTagAndClassName('embed');
            MochiKit.Iter.forEach(embed, function(e){
                MochiKit.DOM.hideElement(e);
            });
    });
    connect(MochiKit.DragAndDrop.Draggables, 'onEnd', function(evt){
            var embed = getElementsByTagAndClassName('embed');
            MochiKit.Iter.forEach(embed, function(e){
                MochiKit.DOM.showElement(e);
            });
    });
}

MochiKit.DOM.addLoadEvent(initialize_dashboard);

// vim: sts=4 st=4 et

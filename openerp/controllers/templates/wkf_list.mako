<%inherit file="master.mako"/>
<%! show_header_footer = False %>
<%def name="header()">
    <title>${_("Manage Workflows %s") % (model)}</title>
    <script type="text/javascript">
    
        function do_select(id, src){
            var radio = MochiKit.DOM.getElement(src + '/' + id);
			if (radio) {
				radio.checked = true;
			}
        }
        
        function doCreate() {
            var vf = document.forms['view_form'];
            vf.submit();
        }
        
        function doCancel() {
            var edt = getElement('view_editor');
            var lst = getElement('view_list');
            
            edt.style.display = "none";
            lst.style.display = "";
        }
        
        function doClose() {
            window.opener.setTimeout("window.location.reload()", 0);
            window.close();
        }
        
        function onNew() {
            var edt = getElement('view_editor');
            var lst = getElement('view_list');
            
            var nm = getElement('name');
            nm.value = getElement('model').value + '.custom_' + Math.round(Math.random() * 1000);
            
            var osv = getElement('osv')
            osv.value = getElement('model').value
            
            edt.style.display = "";
            lst.style.display = "none";
        }
        
        function onEdit() {
            
            var list = new ListView('_terp_list');
            var boxes = list.getSelectedItems();

            if (boxes.length == 0){
                alert(_('Please select a workflow...'));
                return;
            }
            
            openWindow(getURL('/workflow', {model: getElement('model').value, id:boxes[0].value }));
        }
        
        function onRemove() {
        
            var list = new ListView('_terp_list');
            var boxes = list.getSelectedItems();

            if (boxes.length == 0){
                alert(_('Please select a workflow...'));
                return;
            }
            
            if (!window.confirm(_('Do you really want to remove this workflow?'))){
                return;
            }
            
            window.location.href = '/workflowlist/delete?model=${model}&id=' + boxes[0].value;
        }
        
        function onActivate() {
            var list = new ListView('_terp_list');
            var boxes = list.getSelectedItems();

            if (boxes.length == 0){
                alert(_('Please select a workflow...'));
                return;
            }
            
            window.location.href = '/workflowlist/activate?model=${model}&id=' + boxes[0].value;
        }
		
		MochiKit.DOM.addLoadEvent(function(evt){
            
            if (!window.opener) 
                return;
            
            try {
                do_select(parseInt('${active}'), '_terp_list');
            } catch(e){}
        });
        
    </script>
</%def>

<%def name="content()">
    <table id="view_list" class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="${py.url('/static/images/stock/gtk-find.png')}"/>
                        </td>
                        <td width="100%">${_("Manage Workflows %s") % (model)}</td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>${screen.display()}</td>
        </tr>
        <tr>
            <td>
                <div class="toolbar">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td>
                                <button type="button" onclick="onNew()">${_("New")}</button>
                                <button type="button" onclick="onEdit()">${_("Edit")}</button>
                                <button type="button" onclick="onRemove()">${_("Remove")}</button>
                                <button type="button" onclick="onActivate()">${_("Activate")}</button>
                            </td>
                            <td width="100%"></td>
                            <td>
                                <button type="button" onclick="doClose()">${_("Close")}</button>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
    
    <table id="view_editor" style="display: none;" class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="${py.url('/static/images/stock/gtk-edit.png')}"/>
                        </td>
                        <td width="100%">${_("Create a Workflow (%s)") % (model)}</td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <form id="view_form" action="/workflowlist/create">
                    <input type="hidden" id="model" name="model" value="${model}"/>
                    <table width="400" align="center" class="fields">
                        <tr>
                            <td class="label">${_("Workflow Name:")}</td>
                            <td class="item"><input type="text" id="name" name="name" class="requiredfield"/></td>
                        </tr>
                        <tr>
                            <td class="label">${_("Resource Model:")}</td>
                            <td class="item"><input type="text" id="osv" name="osv" class="readonlyfield"/></td>
                        </tr>
                        <tr>
                            <td class="label">${_("On Create:")}</td>
                            <td class="item"><input id="on_create" name="on_create" class="checkbox" type="checkbox" checked=""/></td>                           
                        </tr>
                    </table>
                </form>
            </td>
        </tr>
        <tr>
            <td>
                <div class="toolbar">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td width="100%"></td>
                            <td>
                                <button type="button" onclick="doCreate()">${_("Save")}</button>
                                <button type="button" onclick="doCancel()">${_("Cancel")}</button>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
</%def>

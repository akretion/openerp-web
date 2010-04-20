<%
# put in try block to prevent improper redirection on connection refuse error
try:
    ROOT = cp.request.pool.get_controller("/")
    SHORTCUTS = cp.request.pool.get_controller("/shortcuts")
    REQUESTS = cp.request.pool.get_controller("/requests")
    
    shortcuts = SHORTCUTS.my()
    requests, requests_message = REQUESTS.my()
except:

    ROOT = None
    
    shortcuts = []
    requests = []
    requests_message = None
%>

<script type="text/javascript">

 	function show_process_view() {
		var f = window.frames["appFrame"]
		
		if (f.location == 'about:blank'){
			alert('Please open menu for detail help...')
			return;
		}
		
		var frame = f.document.view_form;
		var model = frame._terp_model.value;
		var id = frame._terp_id.value;
		 	
	 	if (frame._terp_list) {
			var ids = frame._terp_checked_ids.value;
	      	if (ids.length) {
				id = ids[0];
	      	}
	 	}
		id = parseInt(id) || null;    	
		f.location.href = openobject.http.getURL('/process', {res_model: model, res_id: id})
	}
	
</script>
<table id="header" class="header" cellpadding="0" cellspacing="0" border="0">
    <tr>
        <td rowspan="2">
        <img src="/openerp/static/images/openerp_big.png" 
            alt="OpenERP" border="0" width="200" height="60" usemap="#logo_map"/>
            <map name="logo_map">
                <area shape="rect" coords="102,42,124,56" href="http://openerp.com" target="_blank"/>
                <area shape="rect" coords="145,42,184,56" href="http://axelor.com" target="_blank"/>
            </map>
        </td>
        <td align="right" valign="top" nowrap="nowrap" height="24">
            <table class="menu_connection" cellpadding="0" cellspacing="0" border="0">
                <tr>
                    <td width="26" class="menu_connection_right" nowrap="nowrap">
                        <div style="width: 26px;"></div>
                    </td>
                    <td class="menu_connection_welcome" nowrap="norwap">
                        ${_("Welcome %(user)s", user=rpc.session.user_name or 'guest')}
                    </td>
                    <td class="menu_connection_links" nowrap="norwap">
                        <a href="${py.url('/logout')}" target="_top">${_("Logout")}</a>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    <tr>
        <td align="right" valign="middle" style="padding-right: 4px;">
        	<table border="0" cellpadding="0" cellspacing="0">
        		<tr>
        			<td nowrap="nowrap">
			            <a target='appFrame' href="${py.url('/home')}">
			            	<img src="/openerp/static/images/stock/gtk-home.png" style="padding: 4px;" title="Home" border="0" width="16" height="16"/>
			            </a>
			        </td>
			        % if rpc.session.is_logged():
			        <td nowrap="nowrap">
			            <table id="shortcuts" class="menubar" border="0" cellpadding="0" cellspacing="0">
			                <tr>
			                    <td id="shortcuts_menu" nowrap="nowrap">
			                        <a href="javascript: void(0)">
						            	<img src="/openerp/static/images/shortcut.png" id="show_shortcut" style="padding: 1px;" border="0" width="18" height="18"/>
						            </a>
						             <script type="text/javascript">
			                        		jQuery('[id=show_shortcut]').mouseover(function() {
			                        			jQuery.post('/shortcuts/get_shortcuts',
			                        				function(xmlHttp) {
			                        					jQuery('[id=shortcuts_submenu]').html(xmlHttp);
			                        				}
			                        			);
			                        			
			                        		});
		                        	</script> 
			                        <div class="submenu" id="shortcuts_submenu">
			                            % for sc in shortcuts:
			                            <a target='appFrame' href="${py.url('/tree/open', id=sc['res_id'], model='ir.ui.menu')}" style="height: 10px; padding: 0 2px 8px 5px;">
			                            	${sc['name']}
			                            </a>
			                            % endfor
			                            <hr id="shortcut_sep" style="border: none; border-top: dashed 1px #CCCCCC; color: #FFFFFF; background-color: #FFFFFF; height: 1px; padding: 0"/>
			                            <a id="manage_shortcuts" target='appFrame' href="/shortcuts" style="height: 10px; padding: 0 2px 8px 5px;">${_("Manage Shortcuts")}</a>
			                        </div>
			                    </td>
			                </tr>
			            </table>
			            <script type="text/javascript">
			                new Menu('shortcuts_menu', 'shortcuts_submenu');
			            </script>
			        </td>
			        % endif
			        <td nowrap="nowrap">
			        	<a target='appFrame' href="javascript: void(0)">
			            	<img src="/openerp/static/images/inbox.png" style="padding: 4px;" title="Inbox" border="0" width="16" height="16"/>
			            </a>
			        </td>
			        <td nowrap="nowrap">
			            <a target='appFrame' href="${py.url('/pref/create')}">
			            	<img src="/openerp/static/images/preferences.png" style="padding: 4px;" title="Preference" border="0" width="16" height="16"/>
			            </a>
			        </td>
			        <!--<td nowrap="nowrap">
			            <a target='appFrame' href="javascript: void(0)">
			            	<img src="/openerp/static/images/share.png" style="padding: 4px;" title="Share" border="0" width="18px" height="18px"/>
			            </a>
			        </td> -->
			        <td nowrap="nowrap">
			            <a target='appFrame' onclick="show_process_view()">
			            	<img src="/openerp/static/images/stock/gtk-help.png" style="padding: 4px;" title="Help" border="0" width="16" height="16"/>
			            </a>
			        </td>
			        <td nowrap="nowrap">
			            <a target='appFrame' href="${py.url('/about')}">
			            	<img src="/openerp/static/images/about.png" style="padding: 4px;" title="About" border="0" width="18" height="18"/>
			            </a>
			        </td>
			    </tr>
			</table>
    	</td>
    </tr>
</table>

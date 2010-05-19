<%
# put in try block to prevent improper redirection on connection refuse error
try:
    ROOT = cp.request.pool.get_controller("/")
    SHORTCUTS = cp.request.pool.get_controller("/shortcuts")
    REQUESTS = cp.request.pool.get_controller("/requests")
    
    shortcuts = SHORTCUTS.my()
    requests, requests_message, total_mess = REQUESTS.my()
except:

    ROOT = None
    
    shortcuts = []
    requests = []
    requests_message = None
%>

<script type="text/javascript">
	jQuery(document).ready(function() {
		var top_divWidth = jQuery('div#top-menu').width();
		var logoWidth = jQuery('p#logo').width();
		
		var sc_rowWidth = top_divWidth - logoWidth - 20;
		jQuery('tr#sc_row').css('width', sc_rowWidth);
	});
	
	jQuery(window).resize(function() {
		var top_divWidth = jQuery('div#top-menu').width();
		var logoWidth = jQuery('p#logo').width();
		
		var sc_rowWidth = top_divWidth - logoWidth - 20;
		jQuery('tr#sc_row').css('width', sc_rowWidth);
	});
	
</script>
			
<div id="top">
	<div id="top-menu">
		<p id="logo">
			<a href="javascript: void(0)" accesskey="h">
				<img src="/openerp/static/images/logo-a.gif" width="83px" height="26px"/>
			</a>
		</p>
		<h1 id="title-menu">Tiny SPRL <small>Administration</small></h1>
		<ul id="skip-links">
			<li><a href="#nav" accesskey="n">Skip to navigation [n]</a></li>
			<li><a href="#content" accesskey="c">Skip to content [c]</a></li>
			<li><a href="#footer" accesskey="f">Skip to footer [f]</a></li>
		</ul>
		<div id="corner">
			<p class="name">${_("%(user)s", user=rpc.session.user_name or 'guest')}</p>
			<ul class="tools">
				<li>
					% if rpc.session.is_logged():
						<a target='appFrame' href="${py.url('/requests')}" class="messages">Messages<small>${total_mess}</small></a>
					% endif
				</li>
				<li><a href="${py.url('/')}" class="home">Home</a></li>
				
				<li><a href="javascript: void(0)" class="preferences">Preferences</a>
					<ul>
						<li class="first last">
							<a target='appFrame' href="${py.url('/pref/create')}">Edit Preferences</a>
						</li>
					</ul>
				</li>
				<li><a href="javascript: void(0);" class="help">Help</a></li>
				<li><a href="javascript: void(0);" class="info">Info</a></li>
			</ul>
			<p class="logout"><a href="${py.url('/logout')}" target="_top">${_("Logout")}</a></p>
		</div>
	</div>
	
	% if rpc.session.is_logged():
	    <table id="shortcuts" class="menubar" cellpadding="0" cellspacing="0">
	        <tr id="sc_row">
	            % for i, sc in enumerate(shortcuts):
	                % if i<6:
			            <td nowrap="nowrap">
			                <a target="appFrame" href="${py.url('/tree/open', id=sc['res_id'], model='ir.ui.menu')}">${sc['name']}</a>
			            </td>
	                % endif
	            % endfor
	            % if len(shortcuts)>6:
	            <td id="shortcuts_menu" nowrap="nowrap" style="border-right: 1px solid #CCCCCC;">
	                <a style="padding-left: 5px;" href="javascript: void(0)">>></a>
	                <div class="submenu" id="shortcuts_submenu" style="display: none;">
	                    % for sc in shortcuts[6:]:
	                    <a style="float: none; padding: 6px 5px 6px 2px;" target="appFrame" href="${py.url('/tree/open', id=sc['res_id'], model='ir.ui.menu')}">${sc['name']}</a>
	                    % endfor
	                </div>
	            </td>
	            % endif
	            <td id="manage_sc" style="width: 60%; border-right: 0;">
	            	<a style="float: none; text-align: right;" target='appFrame' href="/shortcuts">Edit</a>
	            </td>
	        </tr>
	    </table>
	    % if len(shortcuts)>6:
	    <script type="text/javascript">
	        new Menu('shortcuts_menu', 'shortcuts_submenu');
	    </script>
	    % endif
	% endif
</div>

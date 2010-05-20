<%def name="sidebox_action_item(item, model, submenu)">
    % if submenu != 1:
	    <li onclick="do_action(${item['id']}, '_terp_id', '${model}', this);">
	    	<a href="javascript: void(0)" onclick="return false">${item['name']}</a>
	    </li>
	% else:
		<%
			from openobject import icons
		%>
		<li data="${item}">
	   		% if item['name']:
				<a href="#" onclick="submenu_action('${item['action_id']}', '${model}');">
					${item['name']}
				</a>
			% endif
		</li>
	% endif
</%def>

<%def name="make_sidebox(title, model, items, submenu=0)">

<h4 class="a">${title}</h4>
<ul class="clean-a">
	% for item in items:
        % if item:
        	${sidebox_action_item(item, model, submenu)}
        % endif
    % endfor
</ul>
</%def>

% if reports or actions or relates or attachments:
<form id="attachment-box" name="attachment-box" action="/form/save_attachment" method="post" enctype="multipart/form-data">
<div>
	<table style="height: 150px;">
		<thead style="border-bottom: 1px solid silver;">
			<tr>
				<td colspan="2">
					<div id="header-message" class="attachment-header" style="text-align: center;">Add an Attachment</div>
				</td>
			</tr>
		</thead>
		<tbody style="border-bottom: 1px solid silver;">
		<tr>
			<td>
				<div>File:</div>
			</td>
			<td>
				<div id="datas_binary_add">
					<input type="file" id="datas" class="binary" onchange="onChange(this); set_binary_filename(this, 'datas_fname');" name="datas" kind="binary" size="20"/>
				</div>
			</td>
		</tr>
		<tr>
			<td>
				<div>Attachment Name:</div>
			</td>
			<td>
				<div id="file-name">
					<input id="datas_fname" type="text" maxlength="64" name="datas_fname" kind="char" class="char"/>
				</div>
			</td>
		</tr>
		</tbody>
		<tfoot style="border-bottom: 1px solid silver; vertical-align: middle;">
			<tr>
				<td colspan="2" style="text-align: right;">
					<input type="submit" id="FormSubmit" value="save">
					<input type="button" id="FormCancel" value="cancel">
				</td>
			</tr>
		</tfoot>
	</table>
</div>
</form>

<table id="sidebar_pane" border="0" cellpadding="0" cellspacing="0">
    <tr>
        <td id="sidebar" style="display: none">
			<div class="sideheader-a">
				<h2>Secondary Options</h2>
			</div>
            % if reports:
                ${make_sidebox(_("REPORTS"), model, reports)}
            % endif

            % if actions:
                ${make_sidebox(_("ACTIONS"), model, actions)}
            % endif

            % if relates:
                ${make_sidebox(_("LINKS"), model, relates)}
            % endif

            % if sub_menu:
                ${make_sidebox(_("SUBMENU"), model, sub_menu, submenu=1)}
            % endif
        </td>

		<td id="sidebar_hide" style="padding : 0px; border-color: #EAE7E7;" valign="top">
			<p class="toggle-a"><a id="toggle-click" href="javascript: void(0)" onclick="toggle_sidebar();">Toggle</a></p>
        </td>
    </tr>
    <tr>
    	<td id="attach_sidebar" colspan='2' style="display: none;">
    		% if attachments:
            	<div class="sideheader-a">
					<ul class="side">
						<li><a href="javascript: void(0);" id="add-attachment" class="button-a">Add</a></li>
					</ul>
					<h2>Attachments</h2>
					<script type="text/javascript">
						jQuery('#add-attachment').click(function() {
							jQuery.blockUI({
								css: {border: 'none', opacity: .9},
								message: jQuery('#attachment-box'),
								fadeIn: 1000,
								fadeOut: 1000
							});
						});
					</script>
				</div>
				<ul class="attachments-a">
					% for item in attachments:
						<li>
							<a href="${py.url(['/attachment/save_as', item[1]], record=item[0])}">
								${item[1]}
							</a>
							<span>|</span>
							<a href="javascript: void(0);" class="close" title="${_('Delete')}" onclick="removeAttachment(${item[0]});">Close</a>
						</li>
					% endfor
				</ul>
            % endif
    	</td>
    </tr>
</table>
<script type="text/javascript">
                       
   jQuery('#FormCancel').click(function() {
        jQuery.unblockUI();
    });
    
    jQuery('#datas').validate({
         expression: "if (VAL) return true; else return false;",
         message: "enter the attachment file"
    });
   
     jQuery("#datas_fname").validate({
         expression: "if (VAL) return true; else return false;",
         message: "enter the attachment name"
    });
</script>
% endif


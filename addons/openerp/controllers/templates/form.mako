<%inherit file="/openerp/controllers/templates/base.mako"/>

<%def name="header()">
    <title>${form.screen.string}</title>

    <script type="text/javascript">
        var form_controller = '${path}';
    </script>

    <script type="text/javascript">
    
        function do_select(id, src) {
            viewRecord(id, src);
        }

    </script>
</%def>

<%def name="content()">

    <table id="main_form_body" class="view" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
            <td id="body_form_td" width="100%" valign="top">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    % if buttons.toolbar:
                    <tr>
                        <td>
                            <table width="100%" id="title_header">
                                <tr>
                                    <td width="50%" style="padding: 0px 5px 1px 0px;">
                                    	<h1>${form.screen.string}</h1>
                                    </td>
                                    
                                    <%def name="make_view_button(i, kind, name, desc, active)">
                                    	<li class="v${i}" title="${desc}">
                                    		% if form.screen.view_type == kind:
                                    			<a href="javascript: void(0);" onclick="switchView('${kind}')" class="active">${kind}</a>
                                    		% else:
                                    			<a href="javascript: void(0);" onclick="switchView('${kind}')">${kind}</a>
                                    		% endif
                                    	</li>
                                    </%def>
                                   
                                    <td id="view_buttons" style="padding: 0px 5px 0px 0px;">
                                    	<ul class="views-a">
                                    		% for i, view in enumerate(buttons.views):
												${make_view_button(i+1, **view)}
											% endfor
										</ul>
									</td>
									
									<td style="padding: 0px 5px 0px 0px; cursor: pointer;">
                                    % if buttons.process:
                                    	 <a target="_blank" onclick="show_process_view()">
                                    	 	<img title="${_('Corporate Intelligence...')}" class="button" border="0" src="/openerp/static/images/stock/gtk-help.png" width="16" height="16"/>
                                    	 </a>
                                    % endif
                                    </td>
                                  
                                    % if buttons.can_attach and not buttons.has_attach:
                                    <td align="center" valign="middle" width="16" style="padding: 0px 5px 0px 0px;">
                                        <img 
                                            class="button" width="16" height="16"
                                            title="${_('Show attachments.')}" 
                                            src="/openerp/static/images/stock/gtk-paste.png" 
                                            onclick="window.open(openobject.http.getURL('/attachment', {model: '${form.screen.model}', id: ${form.screen.id}}))"/>
                                    </td>
                                    % endif
                                    % if buttons.can_attach and buttons.has_attach:
                                    <td align="center" valign="middle" width="16" style="padding: 0px 5px 0px 0px;">
                                        <img
                                            class="button" width="16" height="16"
                                            title="${_('Show attachments.')}" 
                                            src="/openerp/static/images/stock/gtk-paste-v.png" onclick="window.open(openobject.http.getURL('/attachment', {model: '${form.screen.model}', id: '${form.screen.id}'}))"/>
                                    </td>
                                    % endif
                                    % if form.screen.view_type in ('form'):
                                    <td align="center" valign="middle" width="16" style="padding: 0px 5px 0px 0px;">
                                        <img 
                                            class="button" width="16" height="16"
                                            title="${_('Translate this resource.')}" 
                                            src="/openerp/static/images/stock/stock_translate.png" onclick="openobject.tools.openWindow('${py.url('/translator', _terp_model=form.screen.model, _terp_id=form.screen.id)}')"/>
                                    </td>
                                    % endif
                                    % if form.screen.view_type in ('form'):
                                    <td align="center" valign="middle" width="16" style="padding: 0px 5px 0px 0px;">
                                        <img 
                                            class="button" width="16" height="16"
                                            title="${_('View Log.')}" 
                                            src="/openerp/static/images/stock/stock_log.png"
                                            onclick="openobject.tools.openWindow('${py.url('/viewlog', _terp_model=form.screen.model, _terp_id=form.screen.id)}', {width: 500, height: 300})"/>
                                    </td>
                                    % endif
                                </tr>
                            </table>
                        </td>
                    </tr>
                    % endif

                    % if form.screen.view_type == 'form' and buttons.toolbar:
                    <tr>
                        <td>
                            <div class="wrapper">
                            	<ul class="inline-b left w50">
									% if buttons.new:
		                            <li title="${_('Create a new resource')}">
		                            	<a href="javascript: void(0);" onclick="editRecord(null)" class="button-a">${_("New")}</a>
		                            </li>
	                            	% endif
		                            % if buttons.edit:
		                            <li title="${_('Edit this resource')}"> 
		                                <a href="javascript: void(0);" onclick="editRecord(${form.screen.id or 'null'})" class="button-a">${_("Edit")}</a>
		                            </li>
		                            % endif
		                            % if buttons.save:
		                            <li title="${_('Save this resource')}">
		                                <a href="javascript: void(0);" onclick="submit_form('save')" class="button-a">${_("Save")}</a>
		                            </li>
		                            <li title="${_('Save & Edit this resource')}"> 
		                                <a href="javascript: void(0);" onclick="submit_form('save_and_edit')" class="button-a">${_("Save & Edit")}</a>
		                            </li>
		                            % endif
		                            % if buttons.edit:
		                            <li title="${_('Duplicate this resource')}">
		                                <a href="javascript: void(0);" onclick="submit_form('duplicate')" class="button-a">${_("Duplicate")}</a>
		                            </li>
		                            % endif
		                            % if buttons.delete:
		                            <li title="${_('Delete this resource')}"> 
		                                <a href="javascript: void(0);" onclick="submit_form('delete')" class="button-a">${_("Delete")}</a>
		                            </li>
		                            % endif
		                            % if buttons.cancel:
		                            <li title="${_('Cancel editing the current resource')}"> 
		                                <a href="javascript: void(0);" onclick="submit_form('cancel')" class="button-a">${_("Cancel")}</a>
		                            </li>
		                            % endif
		                    	</ul>
		                    	
		                    	% if buttons.pager:
                                	<p class="paging-a">
						            	${pager.display()}
									</div>
                                % endif
                            </div>
                        </td>
                    </tr>
                    % endif
                    <tr>
                        <td style="padding: 2px">${form.display()}</td>
                    </tr>
                    % if links:
                    <tr>
                        <td class="dimmed-text">
                            [<a onmouseover="showCustomizeMenu(this, 'customise_menu_')" 
                                onmouseout="hideElement('customise_menu_');" href="javascript: void(0)">${_("Customise")}</a>]<br/>
                            <div id="customise_menu_" class="contextmenu" style="position: absolute; display: none;" 
                                 onmouseover="showElement(this);" onmouseout="hideElement(this);">
                                <a title="${_('Manage views of the current object')}" 
                                   onclick="openobject.tools.openWindow('/viewlist?model=${form.screen.model}', {height: 400})" 
                                   href="javascript: void(0)">${_("Manage Views")}</a>
                                <a title="${_('Manage workflows of the current object')}" 
                                   onclick="openobject.tools.openWindow('/workflowlist?model=${form.screen.model}&active=${links.workflow_manager}', {height: 400})" 
                                   href="javascript: void(0)">${_("Manage Workflows")}</a>
                                <a title="${_('Customise current object or create a new object')}" 
                                   onclick="openobject.tools.openWindow('/viewed/new_model/edit?model=${form.screen.model}')" 
                                   href="javascript: void(0)">${_("Customise Object")}</a>
                            </div>
                        </td>
                    </tr>
                    % endif
                </table>
            </td>

            % if form.sidebar and buttons.toolbar and form.screen.view_type not in ('calendar', 'gantt'):
            <td id="main_sidebar" valign="top">
            	<div id="tertiary">
					<div id="tertiary_wrap">
                		${form.sidebar.display()}
                	</div>
                </div>
            </td>
            % endif
        </tr>
    </table>
</%def>

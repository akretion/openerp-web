<%inherit file="/openobject/controllers/templates/base.mako"/>

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

    <%include file="header.mako"/>

    <table class="view" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
            <td width="100%" valign="top">
                <table cellpadding="0" cellspacing="0" border="0" width="100%">
                    % if buttons.toolbar:
                    <tr>
                        <td>
                            <table width="100%" class="titlebar">
                                <tr>
                                    <td width="32px" align="center">
                                        % if form.screen.view_type in ('tree', 'graph'):
                                        <img src="${cp.static('base', 'images/stock/gtk-find.png')}"/>
                                        % elif form.screen.view_type in ('form'):
                                        <img src="${cp.static('base', 'images/stock/gtk-edit.png')}"/>
                                        % elif form.screen.view_type in ('calendar', 'gantt'):
                                        <img src="${cp.static('base', 'images/stock/stock_calendar.png')}"/>
                                        % endif
                                    </td>
                                    <td width="100%">${form.screen.string}</td>
                                    % if buttons.search or buttons.form or buttons.calendar or buttons.gantt or buttons.graph:
                                    <td nowrap="nowrap">
                                        <button 
                                            type="button" 
                                            title="${_('Tree View...')}" 
                                            ${py.attr_if("disabled",not buttons.search)}
                                            onclick="switchView('tree')">${_("Search")}</button>
                                        <button 
                                            type="button" 
                                            title="${_('Form View...')}" 
                                            ${py.attr_if("disabled",not buttons.form)}
                                            onclick="switchView('form')">${_("Form")}</button>
                                        <button 
                                            type="button" 
                                            title="${_('Calendar View...')}" 
                                            ${py.attr_if("disabled",not buttons.calendar)}
                                            onclick="switchView('calendar')">${_("Calendar")}</button>
                                        <button 
                                            type="button" 
                                            title="${_('Gantt View...')}"
                                            ${py.attr_if("disabled",not buttons.gantt)}
                                            onclick="switchView('gantt')">${_("Gantt")}</button>
                                        <button 
                                            type="button" 
                                            title="${_('Graph View...')}" 
                                            ${py.attr_if("disabled",not buttons.graph)}
                                            onclick="switchView('graph')">${_("Graph")}</button>
                                        % if buttons.process:
                                        <button 
                                            type="button" 
                                            title="${_('Corporate Intelligence...')}"
                                            onclick="show_process_view()">${_("Process")}</button>
                                        % endif
                                    </td>
                                    % endif
                                    % if buttons.can_attach and not buttons.has_attach:
                                    <td align="center" valign="middle" width="16">
                                        <img 
                                            class="button" width="16" height="16"
                                            title="${_('Show attachments.')}" 
                                            src="${cp.static('base', 'images/stock/gtk-paste.png')}" 
                                            onclick="window.open(openobject.http.getURL('/attachment', {model: '${form.screen.model}', id: ${form.screen.id}}))"/>
                                    </td>
                                    % endif
                                    % if buttons.can_attach and buttons.has_attach:
                                    <td align="center" valign="middle" width="16">
                                        <img
                                            class="button" width="16" height="16"
                                            title="${_('Show attachments.')}" 
                                            src="${cp.static('base', 'images/stock/gtk-paste-v.png')}" onclick="window.open(openobject.http.getURL('/attachment', {model: '${form.screen.model}', id: '${form.screen.id}'}))"/>
                                    </td>
                                    % endif
                                    % if form.screen.view_type in ('form'):
                                    <td align="center" valign="middle" width="16">
                                        <img 
                                            class="button" width="16" height="16"
                                            title="${_('Translate this resource.')}" 
                                            src="${cp.static('base', 'images/stock/stock_translate.png')}" onclick="openobject.tools.openWindow('${py.url('/translator', _terp_model=form.screen.model, _terp_id=form.screen.id)}')"/>
                                    </td>
                                    % endif
                                    % if form.screen.view_type in ('form'):
                                    <td align="center" valign="middle" width="16">
                                        <img 
                                            class="button" width="16" height="16"
                                            title="${_('View Log.')}" 
                                            src="${cp.static('base', 'images/stock/stock_log.png')}"
                                            onclick="openobject.tools.openWindow('${py.url('/viewlog', _terp_model=form.screen.model, _terp_id=form.screen.id)}', {width: 500, height: 300})"/>
                                    </td>
                                    % endif
                                    <td align="center" valign="middle" width="16">
                                        <a target="_blank" href="${py.url('http://doc.openerp.com/index.php', model=form.screen.model, lang=rpc.session.context.get('lang', 'en'))}">
                                            <img title="Help links might not work. We will setup the new documentation once we ported all docs to the new documentation system." class="button" border="0" src="${cp.static('base', 'images/stock/gtk-help.png')}" width="16" height="16"/>
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    % endif

                    % if form.screen.view_type == 'form' and buttons.toolbar:
                    <tr>
                        <td>
                            <div class="toolbar">
                                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                                    <tr>
                                        <td>
                                            % if buttons.new:
                                            <button 
                                                type="button" 
                                                title="${_('Create a new resource')}" 
                                                onclick="editRecord(null)">${_("New")}</button>
                                            % endif
                                            % if buttons.edit:
                                            <button 
                                                type="button" 
                                                title="${_('Edit this resource')}" 
                                                onclick="editRecord(${form.screen.id or 'null'})">${_("Edit")}</button>
                                            % endif
                                            % if buttons.save:
                                            <button 
                                                type="button" 
                                                title="${_('Save this resource')}"
                                                onclick="submit_form('save')">${_("Save")}</button>
                                            <button 
                                                type="button" 
                                                title="${_('Save & Edit this resource')}" 
                                                onclick="submit_form('save_and_edit')">${_("Save & Edit")}</button>
                                            % endif
                                            % if buttons.edit:
                                            <button 
                                                type="button" 
                                                title="${_('Duplicate this resource')}"
                                                onclick="submit_form('duplicate')">${_("Duplicate")}</button>
                                            % endif
                                            % if buttons.delete:
                                            <button 
                                                type="button"
                                                title="${_('Delete this resource')}" 
                                                onclick="submit_form('delete')">${_("Delete")}</button>
                                            % endif
                                            % if buttons.cancel:
                                            <button 
                                                type="button" 
                                                title="${_('Cancel editing the current resource')}" 
                                                onclick="submit_form('cancel')">${_("Cancel")}</button>
                                            % endif
                                        </td>
                                        % if buttons.pager:
                                        <td align="right" nowrap="nowrap" class="pager">${pager.display()}</td>
                                        % endif
                                    </tr>
                                </table>
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
            <td width="163" valign="top">
                ${form.sidebar.display()}
            </td>
            % endif
        </tr>
    </table>
    
<%include file="footer.mako"/>    

</%def>

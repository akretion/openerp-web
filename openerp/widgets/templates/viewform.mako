<form method="post" id="${name}" name="${name}" action="${action}" enctype="multipart/form-data">

    <div>
        <input type="hidden" id="_terp_search_domain" name="_terp_search_domain" value="${search_domain}"/>
        <input type="hidden" id="_terp_search_data" name="_terp_search_data" value="${search_data}"/>
    % if show_header_footer:
        <input type="hidden" id="_terp_header_footer" name="_terp_header_footer" value="1" py:if="value_of('show_header_footer', False)"/>
    % endif

    % for field in hidden_fields:
        ${display_member(field)}
    % endfor
    </div>

% if screen:
    <table border="0" cellpadding="0" cellspacing="0" width="100%">
        % if search:
        <tr>
            <td valign="top">${display_member(search)}</td>
        </tr>
        <tr>
            <td style="padding: 3px; padding-top: 0px">
                <div class="toolbar">
                    <button type="button" title="${_('Filter records.')}" onclick="search_filter()">${_("Filter")}</button>
                    % if screen.editable and screen.view_type in ('form', 'tree'):
                    <button type="button" title="${_('Delete selected records.')}"
                        onclick="new ListView('_terp_list').remove()">${_("Delete")}</button>
                    % endif
                    % if screen.editable and screen.view_type in ('form', 'tree'):
                    <button type="button" title="${_('Edit selected records.')}"
                        onclick="editSelectedRecord()">${_("Edit")}</button>
                    % endif
                    % if screen.editable and not (screen.view_type=='tree' and screen.widget.editors):
                    <button type="button" title="${_('Create new record.')}" 
                        onclick="editRecord(null)">${_("New")}</button>
                    % endif
                    % if screen.editable and (screen.view_type=='tree' and screen.widget.editors):
                    <button type="button" title="${_('Create new record.')}" 
                        onclick="new ListView('_terp_list').create()">${_("New")}</button>
                    % endif
                </div>
            </td>
        </tr>
        % endif
        <tr>
            <td valign="top">${display_member(screen)}</td>
        </tr>
    </table>
% endif
</form>


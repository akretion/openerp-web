<form xmlns:py="http://purl.org/kid/ns#" method="post" id="${name}" name="${name}" action="${action}" enctype="multipart/form-data">
    <input type="hidden" id="_terp_limit" name="_terp_limit" value="${limit}"/>
    <input type="hidden" id="_terp_offset" name="_terp_offset" value="${offset}"/>
    <input type="hidden" id="_terp_count" name="_terp_count" value="${count}"/>
    <input type="hidden" id="_terp_search_domain" name="_terp_search_domain" value="${ustr(search_domain)}"/>
    <input type="hidden" id="_terp_search_data" name="_terp_search_data" value="${ustr(search_data)}"/>
    
    <span py:for="field in hidden_fields" py:replace="field.display(value_for(field), **params_for(field))"/>
    
    <table border="0" cellpadding="0" cellspacing="0" width="100%" py:if="screen">
            <tr py:if="search">
                <td valign="top" py:content="search.display(value_for(search), **params_for(search))"></td>
            </tr>
            <tr py:if="search">
                <td style="padding: 3px; padding-top: 0px">                    
                    <div class="toolbar">                        
                        <button type="submit" onclick="submit_search_form('find')">Find</button>
                        <button type="button" py:if="screen.editable and not (screen.view_mode[0]=='tree' and screen.widget.editors)" onclick="submit_form('new')">New</button>
                        <button type="button" py:if="screen.editable and (screen.view_mode[0]=='tree' and screen.widget.editors)" onclick="new ListView('_terp_list').create()">New</button>
                    </div>                    
                </td>
            </tr>
            <tr>
                <td valign="top" py:content="screen.display(value_for(screen), **params_for(screen))"></td>
            </tr>
    </table>
</form>

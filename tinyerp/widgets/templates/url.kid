<span xmlns:py="http://purl.org/kid/ns#" py:strip="">
    <table py:if="editable" width="100%" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td>
                <input type="text" kind="${kind}" name='${name}' id ='${field_id}' value="${value}" class="${field_class}" py:attrs="attrs"/>
            </td>
            <td width="16" style="padding-left: 2px">
                <img width="16" height="16" alt="${_('Go!')}" src="/static/images/stock/gtk-jump-to.png" style="cursor: pointer;" onclick="window.open($('${field_id}').value);"/>
            </td>
         </tr>
     </table>
    <span py:if="editable and error" class="fielderror" py:content="error"/>
    <a py:if="not editable" py:content="value" href="${value}"/>
</span>

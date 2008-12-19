<span xmlns:py="http://purl.org/kid/ns#" py:strip="">
    <table py:if="editable" width="100%" cellpadding="0" cellspacing="0" border="0">
        <tr>
            <td>
                <input type="text" kind="${kind}" id="${field_id}" class="${field_class}" name="${name}" value="${strdate or None}" py:attrs='attrs'/>
                <span class="fielderror" py:if="error" py:content="error"/>
            </td>
            <td width="16" style="padding-left: 2px" py:if="not attrs.get('disabled')">
                <img id="${field_id}_trigger" width="16" height="16" alt="${_('Select')}" src="/static/images/stock/stock_calendar.png" style="cursor: pointer;"/>
            </td>
            <script type="text/javascript" py:if="not attrs.get('disabled')">
                Calendar.setup(
                {
                    inputField : "${field_id}",
                    ifFormat : "${format}",
                    button : "${field_id}_trigger",
                    showsTime: ${str(picker_shows_time).lower()}
                });
               </script>
        </tr>
    </table>
    <span py:if="not editable and strdate" kind="${kind}" id="${name}" value="${value}" py:content="strdate"/>
</span>

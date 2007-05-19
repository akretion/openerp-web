<table border="0" cellpadding="0" cellspacing="0" class="one2many" width="100%" xmlns:py="http://purl.org/kid/ns#">
    <tr>
        <td style="padding: 2px" align='right'>
            <div class="toolbar">
            <table width="100%" border="0" cellpadding="0" cellspacing="0">
                <tr>
                    <td><strong>${screen.string}</strong></td>
                    <td align="right">
                        <button type="button" title="Create new record..." name="${button_name}" onclick="submit_form('save', this)">New</button>
                        <button type="button" title="Delete current record..." disabled="${tg.checker(screen.view_mode[0] == 'tree' or not screen.id)}" name="${button_name}" onclick="submit_form('delete', this)">Delete</button>
                        <button type="button" title="Previous record..." disabled="${tg.checker(screen.view_mode[0] == 'tree')}" name="${button_name}" onclick="submit_form('prev', this)">Prev</button>
                        <button type="button" title="Next record..." disabled="${tg.checker(screen.view_mode[0] == 'tree')}" name="${button_name}" onclick="submit_form('next', this)">Next</button>
                        <button type="button" title="Switch view..." name="${button_name}" onclick="submit_form('switch', this)">Switch</button>
                    </td>
                </tr>
            </table>
            </div>
        </td>
    </tr>
    <tr>
        <td><div class="spacer"></div></td>
    </tr>
    <tr>
        <td py:if="screen">
            <input type="hidden" name="${name}/__id" value="${id}"/>
            ${screen.display()}
        </td>
    </tr>
    <tr>
        <td><div class="spacer"></div></td>
    </tr>
</table>

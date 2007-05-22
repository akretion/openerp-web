<table width="100%" cellpadding="0" cellspacing="0" xmlns:py="http://purl.org/kid/ns#">
    <tr>
        <td>
            <input type="hidden" kind="${kind}" id='${name}' name='${name}' value="${value or None}" py:attrs='attrs' callback="${callback}" onchange="${onchange}; getName(this, '${relation}')"/>
            <input type="text" id ='${name}_text' value="${text}" class="${field_class}"  py:attrs='attrs' onchange="if (!this.value){$('${name}').value=''; $('${name}').onchange();} else {getName('${name}', '${relation}');}"/>
            <span class="fielderror" py:if="error" py:content="error"/>
        </td>
        <td width="2px"><div class="spacer"/></td>
        <td width="75px">
            <button type="button" py:attrs="attrs" 
                domain="${ustr(domain)}" context="${ustr(context)}"
                onclick="wopen(getURL('/many2one/new', {model: '${relation}', m2o: '${name}', domain: getNodeAttribute(this, 'domain'), context: getNodeAttribute(this, 'context')}), 'search', 800, 600)">
                Select
            </button>
        </td>
    </tr>
</table>

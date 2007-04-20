<table width="100%" cellpadding="0" cellspacing="0" xmlns:py="http://purl.org/kid/ns#">
    <tr>
        <td width="100%">
            <input type="hidden" kind="${kind}" id='${name}' name='${name}' value="${value or None}" py:attrs='attrs' callback="${onchange}" onchange="${(onchange or None) and 'onChange(this);'} getName(this, '${relation}')"/>
            <input style="width: 100%" type="text" id ='${name}_text' value="${text}" class="${field_class}"  py:attrs='attrs' onchange="if (!this.value){$('${name}').value=''; $('${name}').onchange();} else {getName('${name}', '${relation}');}"/>
            <span class="fielderror" py:if="error" py:content="error"/>
        </td>
        <td>
            <div class="spacer" />
        </td>
        <td>
            <button type="button" py:attrs="attrs" 
                domain="${ustr(domain)}" context="${ustr(context)}"
                onclick="wopen(getURL('/many2one/new', {model: '${relation}', m2o: '${name}', domain: getNodeAttribute(this, 'domain'), context: getNodeAttribute(this, 'context')}), 'search', 800, 600)">Select</button>
        </td>
    </tr>
</table>

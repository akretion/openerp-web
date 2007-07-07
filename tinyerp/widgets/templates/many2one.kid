<span xmlns:py="http://purl.org/kid/ns#" py:strip="">
    <table py:if="editable" width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td>
                <input type="hidden" id='${name}' name='${name}' value="${value or None}" class="${field_class}" py:attrs='attrs' kind="${kind}" domain="${ustr(domain)}" context="${ustr(context)}" relation="${relation}" callback="${callback}"/>
                <input type="text" id='${name}_text' value="${text}" class="${field_class}"  py:attrs='attrs'/>
                <span class="fielderror" py:if="error" py:content="error"/>
            </td>
            <td width="16">
                <img id='${name}_create' width="16" height="16" alt="New" title="Create a new resource" src="/static/images/file.gif" style="cursor: pointer;"/>
            </td>
            <td width="16" py:if="not attrs.get('disabled') or value">
                <img id='${name}_select' width="16" height="16" alt="Search" title="Search / Open a resource" src="/static/images/find.gif"  style="cursor: pointer;"/>
            </td>
        </tr>
    </table>
    
    <script type="text/javascript" py:if="editable">
        new ManyToOne('${name}');
    </script>
    
    <span py:if="not editable">
        <a href="${tg.query('/form/view', model=relation, id=value)}" py:content="text"/>
    </span>
</span>
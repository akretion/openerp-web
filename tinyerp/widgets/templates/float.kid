<span xmlns:py="http://purl.org/kid/ns#">
    <input type="text" kind="${kind}" name='${name}' id ='${field_id}' style = "width : 100%" value="${value}" class="${field_class}" py:attrs='attrs' callback="${callback}" onchange="${onchange}"/>
    <span class="fielderror" py:if="error" py:content="error"/>
</span>

<span xmlns:py="http://purl.org/kid/ns#">
    <textarea rows="6" name='${name}' id ='${field_id}' style = "width : 100%">${value}</textarea>
    <br py:if="error"/><span class="fielderror" py:if="error" py:content="error"/>
</span>
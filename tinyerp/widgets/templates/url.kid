<span xmlns:py="http://purl.org/kid/ns#">
    
    <script language="javascript">
    function open_win(site){
        var web_site;
        
        if(site.indexOf("://")== -1)
            web_site='http://'+site;
        window.open(web_site);
    }
      
    </script>
    
    <table width="100%">
        <tr>
            <td width="100%">
                <input type="text" kind="${kind}" name='${name}' id ='${field_id}' style="width :100%" value="${value}" class="${field_class}" py:attrs="attrs"/>
            </td>
            <td width="100%">
                <button type="button" onclick="open_win($('${field_id}').value);">Open</button>
            </td>
         </tr>
     </table>
    <span class="fielderror" py:if="error" py:content="error"/>
</span>
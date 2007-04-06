<form method="post" action="${action}" id="${name}" name="${name}" xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">

    <input type="hidden" name="_terp_model" value="${model}"/>
    <input type="hidden" name="_terp_state" value="${state}"/>
    <input type="hidden" name="_terp_id" value="${str(id)}"/>
    <input type="hidden" name="_terp_ids" value="${str(ids)}"/>
    <input type="hidden" name="_terp_view_ids" value="${str(view_ids)}"/>
    <input type="hidden" name="_terp_view_mode" value="${str(view_mode)}"/>
    <input type="hidden" name="_terp_view_mode2" value="${str(view_mode2)}"/>
    <input type="hidden" name="_terp_domain" value="${str(domain)}"/>
    <input type="hidden" name="_terp_context" value="${str(context)}"/>

    <input type="hidden" name="_terp_fields_type" value="${str(form_view.fields_type)}"/>
    <input type="hidden" name="_terp_textid" value="${textid}" py:if="textid"/>
    <input type="hidden" name="_terp_hiddenname" value="${hiddenname}" py:if="hiddenname"/>

    ${form_view.display(value_for(form_view), **params_for(form_view))}
         		
	<div class="spacer"></div>
    <div class="toolbar">
		<table>
			<tr width = "100%">
				<td aligh='left'>Limit</td>
		        <td>
		            <input type="text" value="80" name="limit" id="limit" algin ='left' style="width:60px" />
				</td>

				<td width="30px"></td>

    			<td aligh='left'>Offset</td>
		        <td>
	    	    	<input type="text" value="0" name="offset" id="offset" algin ='left' style="width:60px" />
				</td>

				<td width="100%"></td>

    			<td>
		        	<button type="button" title="Find Records..." onclick="submit_form('find')">Find</button>
				</td>
				<td py:if="not textid">
	    	        <button type="button" title="Cancel..." onclick="submit_form('cancel')">Cancel</button>
    			</td>
    			<td py:if="textid">
	    	        <button type="button" title="Cancel..." onclick="close_form()">Cancel</button>
    			</td>

        		<td py:if="not textid">
		            <button type="button" title="Select Record..." onclick="submit_form('ok')">OK</button>
	    		</td>
	    		<td py:if="textid">
		            <button type="button" title="Select Record..." onclick="setfield('${model}', '${textid}','${hiddenname}')">OK</button>
	    		</td>
    		</tr>
    	</table>
    </div>
    <div class="spacer"></div>
    ${list_view.display(value_for(list_view), **params_for(list_view))}
</form>

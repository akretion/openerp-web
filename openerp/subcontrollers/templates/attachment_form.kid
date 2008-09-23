<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">
<head>
    <title>Attachments</title>
    <script type="text/javascript" src="/static/javascript/attachment.js"></script>
    
</head>
<body>

    <table class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="/static/images/stock/stock-paste.png"/>
                        </td>
                        <td width="100%">Attachments Form</td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <form action="/attachment/save" method="post" enctype="multipart/form-data">
                    <input type="hidden" name="model" value="${model}"/>
                    <input type="hidden" name="id" value="${id}"/>
                    <input type="hidden" name="record" value="${record}"/>
                    <div class="toolbar">
                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                                <td class="label" align="left">Add Resource : </td>
                                <td py:if="fname" width="100%">
                                	<input type="file" id="uploadfile" name="uploadfile"> ${fname} </input>
                                </td>
                                <td py:if="not fname" width="100%"><input type="file" id="uploadfile" name="uploadfile"/></td>                                                                
                            </tr>
                        </table>
                    </div>
                    <table width="100%">
                    	<tr>
                    		<td class="item" align="left">
                    			Description :
                    			<textarea name="description" rows="6">${desc}</textarea>
                    		</td>           		
	                   	</tr>
	                </table>
	                <hr/>
					<table align="center" border='0' width="100%">
						<tr>
							<td align="center">
           						<div style="overflow: scroll; width: 770px; height: 300px;">
           							<img py:if="ext" src="${tg.url('/attachment/get_image', record=record)}"/>
           							<img py:if="not ext" src="/static/images/stock/gtk-cancel.png"/>
           						</div>
           					</td>
           				</tr>
           			</table>
                    
                    <div class="toolbar">
	                    <table border='0' cellpadding='0' cellspacing='0' width="100%">
	    					<tr>
	    						<td width="100%" align="right">
	                                <button type="button" onclick="save_file(form)">Save</button>
	                            </td>
	                            <td>
	                                <button type="button" onclick="history.back()">Cancel</button>
	                            </td>
	    					</tr>
	    				</table>
	    			</div>
                </form>
            </td>
        </tr>
    </table>
    

</body>
</html>

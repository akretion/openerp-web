<%inherit file="base.mako"/>

<%def name="header()">
    <link href="${py.url('/static/css/style.css')}" rel="stylesheet" type="text/css" />
    <title>${title}</title>

    <script type="text/javascript" src="${py.url('/static/javascript/textarea.js')}"></script>
    
    <script type="text/javascript">
        var send_maintenance_request = function() {

            var args = {
                explanation: openobject.dom.get('explanation').value,
                remarks: openobject.dom.get('remarks').value,
                tb: openobject.dom.get('error').value
            }

            var req = openobject.http.postJSON('/errorpage/submit', args);

            req.addCallback(function(obj){

                if (obj.error) {
                    return alert(obj.error);
                }
                
                if (obj.message) {
                    alert(obj.message)
                }

                return history.length > 1 ? history.back() : window.close()
            });
        }
		
		var write_data = function() {
		
			var params = { 
					_terp_all_params: openobject.dom.get('_terp_all_params').value
			}
			
			var req = openobject.http.postJSON('/errorpage/write_data', params);
			
			req.addCallback(function(obj){

                if (obj.error) {
                    return alert(obj.error);
                }
                
                return history.length > 1 ? history.back() : window.close()
            });
		}
		
    </script>
</%def>

<%def name="content()">
	
<%include file="header.mako"/>
	
    <input type="hidden" id="_terp_all_params" name="_terp_all_params" value="${all_params}"/>
    
	<table class="view" border="0" width="100%">
        % if maintenance:
        <tr>
            <td valign="top">
<form id="view_form" onsubmit="return false;">
                <div id="error_page_notebook">
                    <div title="${_('Maintenance')}">
                            % if maintenance['status'] == 'none':
                            <pre>
<b>${_("An unknown error has been reported.")}</b><br/>

<b>${_("You do not have a valid Open ERP maintenance contract !")}</b><br/><br/>
${_("""If you are using Open ERP in production, it is highly suggested to subscribe
a maintenance program.

The Open ERP maintenance contract provides you a bugfix guarantee and an
automatic migration system so that we can fix your problems within a few
hours. If you had a maintenance contract, this error would have been sent
to the quality team of the Open ERP editor.

The maintenance program offers you:
* Automatic migrations on new versions,
* A bugfix guarantee,
* Monthly announces of potential bugs and their fixes,
* Security alerts by email and automatic migration,
* Access to the customer portal.

You can use the link bellow for more information. The detail of the error
is displayed on the second tab.""")}
                            </pre>
                            % elif maintenance['status'] == 'partial':
                            <pre>
<b>${_("An unknown error has been reported.")}</b><br/><br/>

${_("""Your maintenance contract does not cover all modules installed in your system !
If you are using Open ERP in production, it is highly suggested to upgrade your
contract.

If you have developped your own modules or installed third party module, we
can provide you an additional maintenance contract for these modules. After
having reviewed your modules, our quality team will ensure they will migrate
automatically for all futur stable versions of Open ERP at no extra cost.

Here is the list of modules not covered by your maintenance contract:""")}

% for mod in maintenance['uncovered_modules']:
${' * %s\n' % mod}
% endfor
${_("""You can use the link bellow for more information. The detail of the error
is displayed on the second tab.""")}
                            </pre>
                            % elif maintenance['status'] == 'full':
                            <div>
                                <table width="100%">
                                    <tr>
                                        <td colspan="2" align="center">
                                            <strong>${_("Maintenance contract.")}</strong><br/><br/>
                                            <em>${_("Your request will be sent to OpenERP and maintenance team will reply you shortly.")}</em>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="label" width="5%" nowrap="nowrap">${_("Explain what you did:")}</td>
                                        <td class="item">
                                            <textarea id="explanation" class="text" rows="10"/>
                                            <script type="text/javascript">
                                                new ResizableTextarea('explanation');
                                            </script>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td class="label">${_("Other Comments:")}</td>
                                        <td class="item">
                                            <textarea id="remarks" class="text" rows="10"/>
                                            <script type="text/javascript">
                                                new ResizableTextarea('remarks');
                                            </script>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td></td>
                                        <td>
                                            <button class="button" type="button" onclick="send_maintenance_request()">${_("Send to Maintenance Team")}</button>
                                        </td>
                                    </tr>
                                </table>
                            </div>
                            % endif
                    </div>
                    <div title="${_('Application Error!')}">
                        <textarea id="error" class="text" readonly="readonly" style="width: 99%" rows="20">${error}</textarea>
                        <script type="text/javascript">
                            new ResizableTextarea('error');
                        </script>
                    </div>
                </div>
                <script type="text/javascript">
                    new Notebook('error_page_notebook');
                </script>
</form>
            </td>
        </tr>
        % else:        	
            <td valign="top">
            	% if concurrency:
            	<table border="0" cellpadding="0" cellspacing="0" align="center">
            		<tr><td height="15px"/></tr>
					<tr>
						<td class="errorbox" style="padding: 30px;">
							<pre align="center">
<b>${_("Write concurrency warning :")}</b><br/>
${_("""This document has been modified while you were editing it.
Choose:

	- "Cancel" to cancel saving.
	- "Write anyway" to save your current version.""")}
			   				</pre>
			   			</td>
			   		</tr>
			   		<tr><td height="5px"/></tr>
			   		<tr>
			   			<td class="errorbox" align="right">
			   				<button type="button" onclick="history.length > 1 ? history.back() : window.close()">${_("Cancel")}</button>
			   				<button type="button" onclick="write_data()">${_("Write Anyway")}</button>
			   			</td>
			   		</tr>
			   	</table>
			   	% else:
                <table border="0" cellpadding="0" cellspacing="0" align="center">
                    <tr><td height="15px"/></tr>
                    <tr>
                        <td class="errorbox welcome">${title}</td>
                    </tr>
                    <tr><td height="5px"/></tr>
                    <tr>
                        <td class="errorbox" style="padding: 30px;">
                            <pre>${error}</pre>
                        </td>
                    </tr>
                    <tr><td height="5px"/></tr>
                    <tr>
                        <td class="errorbox" align="right">
                            <button type="button" onclick="history.length > 1 ? history.back() : window.close()">OK</button>
                        </td>
                    </tr>
                </table>
                % endif
            </td>
        </tr>
        % endif
    </table>
<%include file="footer.mako"/>    
</%def>

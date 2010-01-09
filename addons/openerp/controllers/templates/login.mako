<%inherit file="/openobject/controllers/templates/base.mako"/>

<%def name="header()">
    <title>${_("Login")}</title>
</%def>

<%def name="content()">

<%include file="header.mako"/>

    <div class="view">

        <br/>

        <center>
            <%doc>
            ${cp.root.developped_by()|n}
            </%doc>
        </center>

        <br/>

        <form action="${py.url(target)}" method="post" name="loginform">
            % for key, value in origArgs.items():
            <input type="hidden" name="${key}" value="${value}"/>
            % endfor
            <input type="hidden" name="login_action" value="login"/>
        
            <div class="box2 welcome">${_("Welcome to OpenERP")}</div>

            <div class="box2">
                <table align="center" cellspacing="2px" border="0">
                    % if dblist is not None:
                    <tr>
                        <td class="label">
                            <span>${_("Server:")}</span>
                        </td>
                        <td>${url}</td>
                    </tr>
                    <tr>
                        <td class="label">${_("Database:")}</td>
                        <td>
                            <select name="db" style="width: 302px;">
                                % for v in dblist or []:
                                <option value="${v}" ${v==db and "selected" or ""}>${v}</option>
                                % endfor
                            </select>
                        </td>
                    </tr>
                    % endif

                    <tr>
                        <td class="label">${_("User:")}</td>
                        <td><input type="text" id="user" name="user" style="width: 300px;" value="${user}"/></td>
                    </tr>
                    
                    <tr>
                        <td class="label">${_("Password:")}</td>
                        <td><input type="password" value="${password}" id="password" name="password" style="width: 300px;"/></td>
                    </tr>
                    <tr>
                        <td></td>
                        <td align="right">
                            % if cp.config('dbbutton.visible', 'openobject-web'):
                            <button type="button" style="white-space: nowrap" tabindex="-1" onclick="location.href='${py.url('/database')}'">${_("Databases")}</button>
                            % endif
                            <button type="submit" style="width: 80px; white-space: nowrap">${_("Login")}</button>
                        </td>
                    </tr>
                </table>                
            </div>            
        </form>
    
        % if message:
        <div class="box2 message" id="message">${message}</div>
        % endif
        
        % if info:
        <div class="information">${info|n}</div>
        % endif
    </div>
<%include file="footer.mako"/>    
</%def>

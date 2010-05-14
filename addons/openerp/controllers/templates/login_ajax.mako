<%inherit file="/openerp/controllers/templates/base.mako"/>

<%def name="header()">
    <title>Login</title>

    <script type="text/javascript">

        var do_login = function(form) {

            if (openobject.http.AJAX_COUNT > 0) {
                return false;
            }

            var user = openobject.dom.get('user').value;
            var password = openobject.dom.get('password').value;

            if (!(user || password)) {
                MochiKit.Visual.Highlight('user', {'startcolor': '#FF6666'});
                MochiKit.Visual.Highlight('password', {'startcolor': '#FF6666'});
                openobject.dom.get('user').focus();
                MochiKit.Style.hideElement('message');
                return false;
            }

            if (!user) {
                MochiKit.Visual.Highlight('user', {'startcolor': '#FF6666'});
                openobject.dom.get('user').focus();
                MochiKit.Style.hideElement('message');
                return false;
            }

            if (!password) {
                MochiKit.Visual.Highlight('password', {'startcolor': '#FF6666'});
                openobject.dom.get('password').focus();
                MochiKit.Style.hideElement('message');
                return false;
            }

            var req = openobject.http.getJSON('/login', {
                'db': openobject.dom.get('db').value,
                'user': user,
                'password': password,
                'tg_format': 'json'
            });

            req.addCallback(function(obj){
                if (obj.result) {
                    openobject.dom.get('password').value = '';
                    window.open(openobject.dom.get('location').value || '/');
                    MochiKit.Style.hideElement('message');
                } else {
                    MochiKit.Visual.appear('message');
                }
            });

            return false;
        }

    </script>
</%def>

<%def name="content()">
    <div class="view">

        <form onsubmit="return do_login()" action="/" method="post" name="loginform">
            <input type="hidden" id="location" name="location" value="${location}"/>
            <input type="hidden" id="db" name="db" value="${db}"/>

            % if style=='ajax_small':
            <table align="center" border="0">
                <tr>
                    <td><strong><label for="user">${_("User:")}</label></strong></td>
                </tr>
                <tr>
                    <td><input type="text" id="user" name="user" style="width: 150px;" value="${user}"/></td>
                </tr>
                <tr>
                    <td><strong><label for="password">${_("Password:")}</label></strong></td>
                </tr>
                <tr>
                    <td><input type="password" value="${password}" id="password" name="password" style="width: 150px;"/></td>
                </tr>
                <tr>
                    <td>
                        <button type="submit" style="width: 80px; white-space: nowrap">${_("Login")}</button>
                    </td>
                </tr>
            </table>
            % endif

            % if style=='ajax':
            <table align="center" cellspacing="2px" border="0">
                <tr>
                    <td class="label"><label for="user">${_("User:")}</label></td>
                    <td><input type="text" id="user" name="user" style="width: 150px;" value="${user}"/></td>
                </tr>
                <tr>
                    <td class="label"><label for="password">${_("Password:")}</label></td>
                    <td><input type="password" value="${password}" id="password" name="password" style="width: 150px;"/></td>
                </tr>
                <tr>
                    <td>&nbsp;</td>
                    <td align="right">
                        <button type="submit" style="width: 80px; white-space: nowrap">${_("Login")}</button>
                    </td>
                </tr>
            </table> 
            % endif

        </form>
        <div id="message" style="display: none; color: red; text-align: center;">${_("Bad username or password!")}</div>

    </div>
</%def>


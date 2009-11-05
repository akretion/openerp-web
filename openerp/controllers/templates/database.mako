<%inherit file="/base/controllers/templates/base.mako"/>

<%def name="header()">
    <title>${form.string}</title>

    <script type="text/javascript" src="${py.url('/static/javascript/openobject/openobject.ui.waitbox.js')}"></script>
    
    <link rel="stylesheet" type="text/css" href="${py.url('/static/css/waitbox.css')}"/>
    <link rel="stylesheet" type="text/css" href="${py.url('/static/css/database.css')}"/>

    <script type="text/javascript">

        var WAITBOX = null;

        MochiKit.DOM.addLoadEvent(function(evt){
            WAITBOX = new openobject.ui.WaitBox();
        });

        var dbView = function(name) {
            window.location.href = "${py.url('/database/')}" + name;
        }

        var on_create = function() {
            MochiKit.Async.callLater(2, function(){
                WAITBOX.show();
            });
            return true;
        }

    </script>
</%def>

<%def name="content()">

<%include file="/base/controllers/templates/header.mako"/>

    <table class="view" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
            <td valign="top">
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="${py.url('/static/images/stock/stock_person.png')}"/>
                        </td>
                        <td width="100%">${form.string}</td>
                        <td nowrap="nowrap">
                            <button type="button" 
                                title="${_('Create new database')}"
                                ${py.disabled(form.name=='create')}
                                onclick="dbView('create')">${_("Create")}</button>
                            <button type="button" 
                                title="${_('Drop database')}"
                                ${py.disabled(form.name=='drop')}
                                onclick="dbView('drop')">${_("Drop")}</button>
                            <button type="button" 
                                title="${_('Backup database')}"
                                ${py.disabled(form.name=='backup')}
                                onclick="dbView('backup')">${_("Backup")}</button>
                            <button type="button" 
                                title="${_('Restore database')}"
                                ${py.disabled(form.name=='restore')}
                                onclick="dbView('restore')">${_("Restore")}</button>
                            <button type="button" 
                                title="${_('Change Administrator Password')}"
                                ${py.disabled(form.name=='password')}
                                onclick="dbView('password')">${_("Password")}</button>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td valign="top" align="center">${form.display()}</td>
        </tr>
    </table>
<%include file="/base/controllers/templates/footer.mako"/>    
</%def>

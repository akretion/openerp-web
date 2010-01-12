<%inherit file="/openerp/controllers/templates/base.mako"/>

<%def name="header()">
    <title>${_("Module Management")}</title>
    <script type="text/javascript">
        var do_select = function(){}
    </script>
</%def>

<%def name="content()">

<%include file="header.mako"/>

    <table class="view" cellpadding="0" cellspacing="0" border="0" width="100%">
        <tr>
            <td valign="top">
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="/openerp/static/images/stock/gtk-find.png"/>
                        </td>
                        <td nowrap="nowrap">Web Modules</td>
                     <tr>
                 </table>
             </td>
         </tr>
         <tr>
             <td valign="top">
                 ${form.screen.display()}
             </td>
         </tr>
    </table>

<%include file="footer.mako"/>       
</%def>


<%inherit file="master.mako"/>

<%def name="header()">
    <title>${_("About the OpenERP Web")}</title>
</%def>

<%def name="content()">

<table class="view" width="100%">
    <tr>
        <td>

<table width="100%">
        <tr>
            <td class="titlebar">${_("OpenERP Web")}</td>
        </tr>
        <tr>
            <td>
            <b>${version}</b>
<p>
${_("Copyright &copy; 2006-TODAY Tiny ERP Pvt. Ltd. All Rights Reserved.")}<br/>
${_("OpenERP is a trademark of the Tiny Company.")}

${_("%(ooweb)s is jointly developed by %(tiny)s and %(axelor)s.",
    ooweb="""<i>OpenERP Web</i>""",
    tiny="""<a target="_blank" href="http://tiny.be">Tiny</a>""",
    axelor="""<a target="_blank" href="http://www.axelor.com/">Axelor</a>""")}
</p>

<p>
${_("Licenced under the terms of %(license)s", license="""<a href="/LICENSE.txt">OpenERP Public License (OEPL) v1.1</a>""")}
</p>

            </td>
        </tr>
        <tr>
            <td width="100%" class="titlebar">${_("About OpenERP")}</td>
        </tr>
        <tr>
            <td>
<p>
${_("""%(openerp)s is a free enterprise-scale software system that is designed to boost
productivity and profit through data integration. It connects, improves and
manages business processes in areas such as sales, finance, supply chain,
project management, production, services, CRM, etc..
""", openerp="""<a target="_blank" href="http://openerp.com">OpenERP</a>""")}
</p>

<p>
${_("""The system is platform-independent, and can be installed on Windows, Mac OS X,
and various Linux and other Unix-based distributions. Its architecture enables
new functionality to be rapidly created, modifications to be made to a
production system and migration to a new version to be straightforward.""")}
</p>

<p>
${_("""Depending on your needs, OpenERP is available through a web or application client.""")}
</p>
            </td>
        </tr>
        <tr>
            <td width="100%" class="titlebar">${_("Links")}</td>
        </tr>
        <tr>
            <td>
<ul>
    <li><a target="_blank" href="http://www.openerp.com/">OpenERP</a></li>
    <li><a target="_blank" href="http://www.axelor.com/">${_("The Axelor Company")}</a></li>
    <li><a target="_blank" href="http://tiny.be/">${_("The Tiny Company")}</a></li>
</ul>
            </td>
        </tr>
   </table>

        </td>
        <td width="170" valign="top" id="sidebar">
            <table cellpadding="0" cellspacing="0" border="0" class="sidebox" width="100%">
                <tr>
                    <td>
                        <table border="0" cellpadding="0" cellspacing="0" width="100%">
                            <tr>
                                <td width="8" style="background: #ac0000"/>
                                <td width="7" style="background-color: #363636"/>
                                <td style="color: white; font-weight: bold; font-size: 12px; background-color: #363636">${_("RESOURCES")}</td>
                                <td width="25" valign="top" style="background: url(/static/images/diagonal_left.gif) no-repeat; background-color: #666666"/>
                                <td width="50" style="background-color: #666666"/>
                            </tr>
                        </table>
                    </td>
                </tr>
                <tr>
                    <td>
                        <a target="_blank" href="http://openerp.com">${_("Homepage")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://openerp.com/documentations.html">${_("Documentation")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://openerp.com/forum">${_("Forum")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://openerp.com/component/option,com_mtree/Itemid,111/">${_("Modules")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://openerp.com/component/option,com_joomlaxplorer/Itemid,132/">${_("Download")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://openerp.com/planet">${_("Planet")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://ondemand.openerp.com">${_("SaaS Offers")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://openerp.com/training.html">${_("Trainings")}</a>
                    </td>
                </tr><tr>
                    <td>
                        <a target="_blank" href="http://openerp.com/services.html">${_("Services")}</a>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>

</%def>

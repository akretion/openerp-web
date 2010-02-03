<%inherit file="/openobject/controllers/templates/base.mako"/>

<%def name="header()">
    <script type="text/javascript" src="/openerp/static/javascript/openerp/openerp.ui.js"></script>
    <script type="text/javascript" src="/openerp/static/javascript/openerp/openerp.ui.tips.js"></script>
    <script type="text/javascript" src="/openerp/static/javascript/ajax_stat.js"></script>
    <script type="text/javascript" src="/openerp/static/javascript/menu.js"></script>
    
    <link rel="stylesheet" type="text/css" href="/openerp/static/css/style.css"/>
    <link rel="stylesheet" type="text/css" href="/openerp/static/css/menu.css"/>
    <link rel="stylesheet" type="text/css" href="/openerp/static/css/tips.css"/>
    
    <!--[if IE]>
    <link rel="stylesheet" type="text/css" href="/openerp/static/css/style-ie.css"/>
    <![endif]-->
    
    <script type="text/javascript">
        
        MochiKit.DOM.addLoadEvent(function(evt){
        
            if (parent && parent.MAIN_WINDOW) {
                parent.setTimeout("onload_frame()", 0);
            }
        });
    </script>
    
    ${self.header()}
</%def>


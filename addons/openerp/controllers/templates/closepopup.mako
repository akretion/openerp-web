<%inherit file="/openerp/controllers/templates/base.mako"/>

<%def name="header()">
    <script type="text/javascript">    
        MochiKit.DOM.addLoadEvent(function(evt){
            if (window.opener) {
                window.opener.location.reload();
                window.close();
            } else {
            	openobject.http.redirect('/blank');
            	window.parent.location.href = '/menu';                
            }
        });
    </script>
</%def>

<%def name="content()">

</%def>

<%inherit file="/openerp/controllers/templates/base_dispatch.mako"/>

<%def name="header()">
    <script type="text/javascript" src="/openobject/static/javascript/MochiKit.js"></script>
    <script type="text/javascript" src="/openobject/static/javascript/MochiKit/Resizable.js"></script>
    <script type="text/javascript" src="/openobject/static/javascript/jQuery/jquery-1.4.2.js"></script>
    <script type="text/javascript">
        jQuery.noConflict();
    </script>
    <script type="text/javascript" src="/openobject/static/javascript/openobject/openobject.base.js"></script>
    <script type="text/javascript" src="/openobject/static/javascript/openobject/openobject.gettext.js"></script>
    <script type="text/javascript" src="/openobject/static/javascript/openobject/openobject.dom.js"></script>
    <script type="text/javascript" src="/openobject/static/javascript/openobject/openobject.http.js"></script>
    <script type="text/javascript" src="/openobject/static/javascript/openobject/openobject.tools.js"></script>
    
    <script type="text/javascript">    
        jQuery(document).ready(function(){
            if(!window.opener && window.top == window) {
                window.location.href = '/openerp';
                return;
            }
            var topWindow;
            if(window.top != window) {
                topWindow = window.top;
                setTimeout(function () {
                    topWindow.closeAction();
                });
            } else {
                topWindow = window.opener;
                setTimeout(close);
            }
            /*
            % if reload:
            */
            var $doc = jQuery(topWindow.document);
            switch($doc.find('#_terp_view_type').val()) {
            	case 'form':
                    var terp_id = jQuery(idSelector('_terp_id'),$doc).val();
                    if(terp_id == "False") {
                    	terp_id = '${active_id}';
                    }
                    if(terp_id == "False" || !terp_id) {
                    	topWindow.location.href = '/openerp';
                    	return;
                    } else {
                    	topWindow.editRecord(terp_id);
                    	return;
                    }
                case 'tree':
                    new topWindow.ListView('_terp_list').reload();
                    return;
            }
            topWindow.location.reload();
            /*
            % endif
            */
        });
    </script>
</%def>

<%def name="content()">

</%def>

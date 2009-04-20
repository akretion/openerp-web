<%inherit file="../../templates/master.mako"/>
<%! show_header_footer = False %>
<%def name="header()">
    <title>${form.screen.string}</title>

    <script type="text/javascript">
        var form_controller = '/viewed/new_field';
    </script>

    <script type="text/javascript">
        MochiKit.DOM.addLoadEvent(function(evt) {

            var lc = parseInt(MochiKit.DOM.getElement('_terp_id').value) || 0;

            if (lc > 0) {
            
                var id = parseInt(getElement('_terp_id').value) || 0;
                
                if (id) {
                    var field = window.opener.document.getElementById('name');
                    var name = getElement('name').value;
                    
                    var op = new Option(name, name); 
                    field.options.add(op);
                    op.selected = 1;
                }
                
                window.close();
            }
        });
    </script>
</%def>

<%def name="content()">
    <table class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="/static/images/stock/gtk-edit.png"/>
                        </td>
                        <td width="100%">${form.screen.string}</td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>${form.display()}</td>
        </tr>
        <tr>
            <td>
                <div class="toolbar">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td width="100%">
                            </td>
                            <td>
                                <button type="button" onclick="window.close()">Close</button>
                                <button type="button" onclick="submit_form('save')">Save</button>
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
</%def>

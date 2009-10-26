<%inherit file="base.mako"/>

<%def name="header()">
    <title>${form.screen.string} </title>

    <script type="text/javascript">
        var form_controller = '/openo2m';
    </script>

    <script type="text/javascript">

        function do_select(id, src) {
            viewRecord(id, src);
        }

        MochiKit.DOM.addLoadEvent(function (evt){

            var pwin = window.opener;
            var pform = pwin.document.forms['view_form'];

            var form = document.forms['view_form'];
            var fields = [];

            var required_attrs = ['id', 'name', 'value', 'kind', 'class', 'domain', 'context', 'relation'];

            MochiKit.Iter.forEach(pform.elements, function(e){

                if (e.name && e.type != 'button' && e.name.indexOf('${params.o2m}') != 0){

                    var attrs = {}
                    MochiKit.Iter.forEach(required_attrs, function(n){
                        if (e.attributes[n]) attrs[n] = e.attributes[n].value;
                    });
                    attrs['type'] = 'hidden';
                    attrs['disabled'] = 'disabled';
                    attrs['value'] = e.value;

                    var fld = MochiKit.DOM.INPUT(attrs);
                    fields = fields.concat(fld);
                }
            });

            MochiKit.DOM.appendChildNodes(form, fields);

            var lc = openobject.dom.get('_terp_load_counter').value;

            lc = parseInt(lc) || 0;

            if (lc > 0) {
                window.opener.setTimeout("new ListView('${params.o2m}').reload(null, 1)", 0.5);
            }

            if (lc > 1) {
                window.close();
            }

        });

    </script>
</%def>

<%def name="content()">
    <table class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
                <input type="hidden" id="_terp_load_counter" value="${params.load_counter}"/>
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="${py.url('/static/images/stock/gtk-edit.png')}"/>
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
                                <button type="button" onclick="window.close()">${_("Close")}</button>
                                % if form.screen.editable:
                                <button type="button" onclick="submit_form('save')">${_("Save")}</button>
                                % endif
                            </td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
</%def>

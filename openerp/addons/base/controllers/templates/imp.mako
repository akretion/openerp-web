<%inherit file="base.mako"/>

<%def name="header()">
    <title>Import Data</title>
    <link href="${py.url('/static/css/listgrid.css')}" rel="stylesheet" type="text/css"/>
    <script type="text/javascript" src="${py.url('/static/javascript/listgrid.js')}"></script>

    <style type="text/css">
        .fields-selector {
            width: 100%;
            height: 300px;
        }

        .fields-selector-left {
            width: 45%;
        }

        .fields-selector-center {
            width: 15%;
        }

        .fields-selector-right {
            width: 45%;
        }

        .fields-selector select {
            width: 100%;
            height: 100%;
        }

        .fields-selector button {
            width: 100%;
            margin: 5px 0px;
        }
    </style>

    <script type="text/javascript">
        function add_fields(){
        
            var tree = ${tree.name};
            
            var fields = tree.selection;
            var select = openobject.dom.get('fields');

            var opts = {};
            forEach(openobject.dom.get('fields').options, function(o){
                opts[o.value] = o;
            });

            forEach(fields, function(f){

                var text = f.record.items.name;
                var id = f.record.id;

                if (id in opts) return;

                select.options.add(new Option(text, id));
            });
        }

        function del_fields(all){

            var fields = filter(function(o){return o.selected;}, openobject.dom.get('fields').options);

            if (all){
                openobject.dom.get('fields').innerHTML = '';
            } else {
                forEach(fields, function(f){
                    removeElement(f);
                });
            }
        }

        function do_import(form){

            var options = openobject.dom.get('fields').options;

            forEach(options, function(o){
                o.selected = true;
            });

            form.target = "detector";

            setNodeAttribute(form, 'action', openobject.http.getURL('/impex/import_data'));
            form.submit();
        }

        function on_detector(src){
            var d = openobject.dom.get("detector");

            if (d.contentDocument)
                d = d.contentDocument;
            else if (d.contentWindow)
                d = d.contentWindow.document;
            else
                d = d.document;

            var f = d.getElementById('fields');

            if (f) {
                openobject.dom.get('fields').innerHTML = '';
                forEach(f.options, function(o){
                    openobject.dom.get('fields').options.add(new Option(o.text, o.value));
                });
            } else {
                f = d.getElementsByTagName('pre');
                if (f[0]) alert(f[0].innerHTML);
            }
        }

        function do_autodetect(form){

            if (! openobject.dom.get('csvfile').value ){
                return alert(_('You must select an import file first!'));
            }

            form.target = "detector";

            setNodeAttribute(form, 'action',openobject.http.getURL('/impex/detect_data'));
            form.submit();
        }

    </script>
</%def>

<%def name="content()">
<form action="/impex/import_data" method="post" enctype="multipart/form-data">

    <input type="hidden" id="_terp_source" name="_terp_source" value="${source}"/>
    <input type="hidden" id="_terp_model" name="_terp_model" value="${model}"/>
    <input type="hidden" id="_terp_ids" name="_terp_ids" value="[]"/>
    <input type="hidden" id="_terp_fields2" name="_terp_fields2" value="[]"/>

    <table class="view" cellspacing="5" border="0" width="100%">
        <tr>
            <td>
                <table width="100%" class="titlebar">
                    <tr>
                        <td width="32px" align="center">
                            <img src="${py.url('/static/images/stock/gtk-go-down.png')}"/>
                        </td>
                        <td width="100%">${_("Import Data")}</td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <table class="fields-selector" cellspacing="5" border="0">
                    <tr>
                        <th class="fields-selector-left">${_("All fields")}</th>
                        <th class="fields-selector-center">&nbsp;</th>
                        <th class="fields-selector-right">${_("Fields to import")}</th>
                    </tr>
                    <tr>
                        <td class="fields-selector-left" height="300px">
                            <div style="overflow: scroll; width: 100%; height: 100%; border: solid #999999 1px;">${tree.display()}</div>
                        </td>
                        <td class="fields-selector-center">
                            <button type="button" onclick="add_fields()">${_("Add")}</button><br/>
                            <button type="button" onclick="del_fields()">${_("Remove")}</button><br/>
                            <button type="button" onclick="del_fields(true)">${_("Nothing")}</button>
                            <br/><br/>
                            <button type="button" onclick="do_autodetect(form)">${_("Auto Detect")}</button>
                        </td>
                        <td class="fields-selector-right" height="300px">
                            <select name="fields" id="fields" multiple="multiple">
                                % for f in fields or []:
                                <option value="${f[0]}">${f[1]}</option>
                                % endfor
                            </select>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        <tr>
            <td>
                <fieldset>
                    <legend>${_("File to import")}</legend>
                    <input type="file" id="csvfile" size="50" name="csvfile" onchange="do_autodetect(form)"/>
                </fieldset>
            </td>
        </tr>
        <tr>
            <td>
                <fieldset>
                    <legend>${_("Options")}</legend>
                    <table>
                        <tr>
                            <td class="label">${_("Separator:")}</td>
                            <td><input type="text" name="csvsep" value=","/></td>
                            <td class="label">${_("Delimiter:")}</td>
                            <td><input type="text" name="csvdel" value='"'/></td>
                        </tr>
                        <tr>
                            <td class="label">${_("Encoding:")}</td>
                            <td>
                                <select name="csvcode">
                                    <option value="utf-8">UTF-8</option>
                                    <option value="latin1">Latin 1</option>
                                </select>
                            </td>
                            <td class="label">${_("Lines to skip:")}</td>
                            <td><input type="text" name="csvskip" value="1"/></td>
                        </tr>
                    </table>
                </fieldset>
            </td>
        </tr>
        <tr>
            <td>
                <div class="toolbar">
                    <table border="0" cellpadding="0" cellspacing="0" width="100%">
                        <tr>
                            <td width="100%">&nbsp;</td>
                            <td><button type="button" onclick="do_import(form)">${_("Import")}</button></td>
                            <td><button type="button" onclick="window.close()">${_("Close")}</button></td>
                        </tr>
                    </table>
                </div>
            </td>
        </tr>
    </table>
</form>

<iframe name="detector" id="detector" style="display: none;" src="about:blank" onload="on_detector(this)"/>
</%def>

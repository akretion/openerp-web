<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="../../templates/master.kid">
<head>
    <title>Search ${screen.string}</title>

    <script type="text/javascript">

        function submit_search_form(action){
            form = $('search_form');
            setNodeAttribute(form, 'action', action);

            disable_hidden_search_fields();

            form.submit();
        }

        function pager_action(action, src){
            if (src)
                new ListView(src).go(action);
           else
                submit_search_form(action);
        }

        function disable_hidden_search_fields(){
            // disable fields of hidden tab

            var hidden_tab = getElementsByTagAndClassName('div', 'tabbertabhide', 'search_form')[0];
            var disabled = [];

            disabled = disabled.concat(getElementsByTagAndClassName('input', null, hidden_tab));
            disabled = disabled.concat(getElementsByTagAndClassName('textarea', null, hidden_tab));
            disabled = disabled.concat(getElementsByTagAndClassName('select', null, hidden_tab));

            forEach(disabled, function(fld){
                fld.disabled = true;
            });

            return true;
        }

    </script>

    <script type="text/javascript" py:if="params.kind == 1">

        function do_select(id){
            if (!id) {
                var ids = new ListView('_terp_list').getSelectedRecords();

                if (ids.length &lt; 1)
                    return;

                id = ids[0];
            }

            value_field = window.opener.document.getElementById('${params.source}');

            value_field.value = id;

            if (!isUndefinedOrNull(value_field.onchange)){
                window.opener.setTimeout("$('${params.source}').onchange()", 0);
               }else{
               window.opener.setTimeout("MochiKit.Signal.signal('${params.source}', 'onchange')", 0);
               }

            window.setTimeout("window.close()", 5);
        }

        function do_create(){
            act = getURL('/openm2o/edit', {model: '${params.model}', source: '${params.source}', id: 'False'});
            window.location.href = act;
        }
    </script>

    <script type="text/javascript" py:if="params.kind == 2">

        function do_select(id) {

            list_view = window.opener.document.getElementById('${params.source}');

            list_view = new ListView(list_view);
            list_this = new ListView('_terp_list');

            ids = list_view.getSelectedRecords();

            if (id){
                if (findValue(ids, id) == -1) ids.push(id);
            } else {
                boxes = list_this.getSelectedItems();

                if(boxes.length == 0) {
                    alert("No record selected...");
                    return;
                }

                forEach(boxes, function(b){
                    if (findValue(ids, b.value) == -1) ids.push(b.value);
                });
            }

            expr = "var m2m = getElement('${params.source}' + '_id');" + "m2m.value = '" + ids.join(',') + "'; m2m.onchange();";
            window.opener.setTimeout(expr, 1);
            window.close();
        }
    </script>
</head>

<body>
<div class="view">
    <form id="search_form" name="search_form" action="/search/find" method="post" onsubmit="return disable_hidden_search_fields();">
        <input type="hidden" id="_terp_source" name="_terp_source" value="${params.source}"/>
        <input type="hidden" id="_terp_kind" name="_terp_kind" value="${params.kind}"/>
        <input type="hidden" id="_terp_limit" name="_terp_limit" value="${screen.limit}"/>
        <input type="hidden" id="_terp_offset" name="_terp_offset" value="${screen.offset}"/>
        <input type="hidden" id="_terp_count" name="_terp_count" value="${screen.count}"/>
        <input type="hidden" id="_terp_search_domain" name="_terp_search_domain" value="${ustr(params.search_domain)}"/>
        <input type="hidden" id="_terp_search_data" name="_terp_search_data" value="${ustr(params.search_data)}"/>

        <table width="100%" border="0" cellpadding="2" xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#">
            <tr>
                <td>
                    <table width="100%" class="titlebar">
                        <tr>
                            <td width="32px" align="center">
                                <img src="/static/images/icon.gif"/>
                            </td>
                            <td width="100%">Search ${screen.string}</td>
                        </tr>
                    </table>
                </td>
            </tr>
            <tr>
                <td py:content="search.display()">Search View</td>
            </tr>
            <tr>
                <td>
                    <div class="toolbar">
                        <button type="submit">Filter</button>
                        <button type="button" onclick="do_create()" py:if="params.kind == 1">New</button>
                        <button type="button" onclick="do_select()">Select</button>
                    </div>
                </td>
            </tr>
            <tr>
                <td py:content="screen.display()">Screen View</td>
            </tr>
        </table>
    </form>
</div>

</body>
</html>

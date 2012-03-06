% if editable:
    <div class = "text">
    % if inline:
        <input id ="${name}" name="${name}" type="text" class="${css_class}" size="1"
            ${py.attrs(attrs, kind=kind, value=value)}/>
    % else:
        <textarea rows="6" id ="${name}" name="${name}" class="${css_class}"
            ${py.attrs(attrs, kind=kind)} style="width: 100%;">${value}</textarea>
        <script type="text/javascript">
            if (!window.browser.isWebKit) {
                new openerp.ui.TextArea('${name}');
            }
        </script>
    % endif
        % if translatable:
         <img name = "${name}" src="/openerp/static/images/stock/stock_translate.png" class="translatable" />
         <script type="text/javascript">
             jQuery('img[name=${name}]').click(function() {
                 var params = {
                     'relation': '${model}',
                     'id': jQuery('#_terp_id').attr('value'),
                     'data': jQuery('#_terp_context').attr('value'),
                 };
                 translate_fields(null, params);
             });
         </script>
    % endif
    % if error:
        <span class="fielderror">${error}</span>
    % endif
    </div>
% else:
    <p kind="${kind}" id="${name}" class="raw-text">${value}</p>
% endif


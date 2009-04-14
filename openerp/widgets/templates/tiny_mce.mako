<textarea id="${name}" name="${name}" kind="${kind}"
    class="${css_class}" style="width: 100%;"
    ${py.attrs(attrs)}>${value}</textarea>
% if editable and error:
<span class="fielderror">${error}</span>
% endif
    
<script type="text/javascript">
    tinyMCE.init({
        mode: "exact",
        elements: "${name}",
        editor_selector: "tinymce",
        readonly: ${(not editable or 0) and 1},
        
        theme: "advanced",

        plugins: "fullscreen,print,safari",
        
        content_css: "${py.url('/static/css/tiny_mce.css')}",
        apply_source_formatting : true,
        
        extended_valid_elements : "a[href|target|name]",

        theme_advanced_disable : "styleselect",
        theme_advanced_toolbar_location : "top",
        theme_advanced_buttons3_add : "|,print,fullscreen",
        theme_advanced_statusbar_location : "bottom",
        theme_advanced_resizing : true,
        theme_advanced_resize_horizontal : false,

        tab_focus : ':prev,:next',
        height: 350,
        debug: false
    });
</script>


% if editable:
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td>
                <input type="hidden" id="${name}" name="${name}" class="${css_class}" value="${value}"
                    ${py.attrs(attrs, kind=kind, domain=domain, context=ctx, relation=relation)}/>
                <input type="text" id="${name}_text" class="${css_class}"
                    ${py.attrs(attrs, kind=kind, relation=relation, value=text)}/>
                % if error:
                <span class="fielderror">${error}</span>
                % endif
            </td>
            <td width="16" style="padding-left: 2px">
                <img id='${name}_open' 
                    width="16" 
                    height="16" 
                    alt="${_('Open')}" 
                    title="${_('Open a resource')}" 
                    src="/static/images/stock/gtk-open.png" 
                    style="cursor: pointer;" 
                    class="imgSelect"/>
            </td>
            <td width="16" style="padding-left: 2px">
                % if readonly:
                <img id='${name}_select'
                    width="16" 
                    height="16" 
                    alt="${_('Search')}" 
                    title="${_('Search')}" 
                    src="/static/images/stock-disabled/gtk-find.png"/>
                % endif
                % if not readonly:
                <img id='${name}_select' 
                    width="16" 
                    height="16" 
                    alt="${_('Search')}" 
                    title="${_('Search')}" 
                    src="/static/images/stock/gtk-find.png" 
                    style="cursor: pointer;" 
                    class="imgSelect"/>
                % endif
            </td>
        </tr>
    </table>
% endif

% if editable:
    <script type="text/javascript">
        new ManyToOne('${name}');
    </script>
% endif

% if not editable and link:
    % if link=='1':
        <span id="${name}" ${py.attrs(kind=kind, value=value, relation=relation, link=link)}>
            <a href="${py.url('/form/view', model=relation, id=value, context=ctx, domain=domain)}">${text}</a>
        </span>
    % endif
    % if link=='0':
        <span id="${name}" ${py.attrs(kind=kind, value=value, relation=relation, link=link)}>${text}</span>
    % endif
% endif

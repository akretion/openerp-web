% if editable:
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td>
                <input type="hidden" id='${name}' name='${name}' value="${value or None}" class="${css_class}" ${py.attrs(attrs)} kind="${kind}" domain="${ustr(domain)}" context="${ustr(context_)}" relation="${relation}"/>
                <select id="${name}_reference" name='${name}'>
                    <option value=""></option>
                    % for (k, v) in options:
                        % if relation == k:
                    <option value="${k}" selected="1">${v}</option>
                        % endif
                    % endfor
                    % for (k, v) in options:
                        % if relation != k:
                    <option value="${k}">${v}</option>
                        % endif
                    % endfor
                </select>
            </td>
            <td>
                <input type="text" id='${name}_text' value="${text}" class="${css_class}"  ${py.attrs(attrs)} kind="${kind}" relation="${relation}"/>
                % if error:
                <span class="fielderror">${error}</span>
                % endif
            </td>
            % if not inline:
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
            % endif
            <td width="16" style="padding-left: 2px">
                <img id='${name}_select' width="16" height="16" alt="${_('Search')}" title="${_('Search')}" src="/static/images/stock/gtk-find.png" style="cursor: pointer;" class="imgSelect"/>
            </td>
        </tr>
    </table>
% endif

% if editable:
    <script type="text/javascript">
        new ManyToOne('${name}');
    </script>    
% else:
    <span>'(%s) %s'%(dict(options).get(relation), text)</span>
% endif


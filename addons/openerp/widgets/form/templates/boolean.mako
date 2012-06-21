% if editable:
    <input
        type="hidden" 
        kind="${kind}" 
        name="${name}" 
        id="${name}" 
        value="${value}"
        ${py.attrs(attrs, fld_readonly=readonly and 1 or 0)}>
    <input
        type="checkbox" 
        kind="${kind}" 
        class="checkbox"
        id="${name}_checkbox_" 
        ${py.checker(value)}
        ${py.attrs(attrs, fld_readonly=readonly and 1 or 0)}>
    % if error:
        <span class="fielderror">${error}</span>
    % endif
% else:
    <input
        type="checkbox"
        kind="${kind}"
        class="checkbox" 
        id="${name}" 
        value="${value}"
        disabled="disabled"
        ${py.checker(value)}>
% endif


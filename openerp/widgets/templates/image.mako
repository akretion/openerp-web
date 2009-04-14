% if stock:
    <img align="left" src="${src}" width="${width}" height="${height}"/>
% endif

% if not stock and id and editable:
    <img 
        id="${field}" 
        border='1' 
        alt="Click here to add new image." 
        align="left" 
        src="${src}" 
        width="${width}" 
        height="${height}" 
        onclick="openWindow(getURL('/image', {model: '${model}', id: ${id}, field : '${field}'}), {width: 500, height: 300});"/>
% endif

% if not stock and id and not editable:
    <img id="${field}" border='1' align="left" src="${src}" width="${width}" height="${height}"/>
% endif

% if not stock and not id and editable:
    <input type="file" class="${field_class}" id="${name}" ${py.attrs(attrs)} name="${name}"/>
% endif

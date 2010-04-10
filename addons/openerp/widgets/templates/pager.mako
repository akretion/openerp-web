<div class="pager">
    <p id="_${name+str(pager_id)}_link_span" class="paging">
        % if prev:
        <a class="first" href="javascript: void(0)" title="first" onclick="pager_action('first', '${name}'); return false;">
        % endif
        <span class="first">${_("<< First")}</span>
        % if prev:
        </a>
        <a class="prev" href="javascript: void(0)" title="previous" onclick="pager_action('previous', '${name}'); return false;">
        % endif
        <span class="prev">${_("< Previous")}</span>
        % if prev:
        </a>
        % endif
        <font onclick="openobject.dom.get('_${name+str(pager_id)}_link_span').style.display='none'; openobject.dom.get('_${name+str(pager_id)}_limit_span').style.display=''" style="cursor: pointer;">${page_info}</font>
        % if next:
        <a class="next" href="javascript: void(0)" title="next" onclick="pager_action('next', '${name}'); return false;">
        % endif
        <span class="next">${_("Next >")}</span>
        % if next:
        </a>
        <a class="last" href="javascript: void(0)" title="last" onclick="pager_action('last', '${name}'); return false;">
        % endif
        <span class="last">${_("Last >>")}</span>
        % if next:
        </a>
        % endif
    </p>

    <table id="_${name+str(pager_id)}_limit_span" style="width: 100%; display: none" border="0" cellpadding="0" cellspacing="0">
        <tr>
            <td align="right">
                <a href="javascript: void(0)" onclick="openobject.dom.get('_${name+str(pager_id)}_limit_span').style.display='none'; openobject.dom.get('_${name+str(pager_id)}_link_span').style.display=''">${_("Change Limit:")}</a>&nbsp;
            </td>
            <td width="45px;">
                <select id='_${name+str(pager_id)}_limit' onchange="openobject.dom.get('${name and (name != '_terp_list' or None) and name + '/'}_terp_limit').value=openobject.dom.get('_${name+str(pager_id)}_limit').value; pager_action('filter', '${name}')">
                    <option value="20" ${py.selector(limit==20)}>20</option>
                    <option value="40" ${py.selector(limit==40)}>40</option>
                    <option value="60" ${py.selector(limit==60)}>60</option>
                    <option value="80" ${py.selector(limit==80)}>80</option>
                    <option value="100" ${py.selector(limit==100)}>100</option>
                </select>
            </td>
        </tr>
    </table>
</div>

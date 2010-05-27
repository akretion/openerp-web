<div class="filter-a">
	<%
		if def_checked:
			filter_class = "active_filter"
			a_class = "active"
		else:
			filter_class = "inactive_filter"
			a_class = "inactive"
			
		if help!=text_val:
			text = text_val
			position = "center top"
		else:
			text = ''
			position = ""
	%>
	<ul>
		<li class="${filter_class}" title="${help}" onclick="search_filter(getElement('${filter_id}'), this);">
			<a class="${a_class}" style="background-image: url(${icon}); background-position: ${position};">
				${text}
				<span>&raquo;</span>
				<input ${py.attrs(attrs)} style="display:none;"
                    type="checkbox"
                    id="${filter_id}"
                    name="${filter_id}"
                    class="${a_class}"
                    onclick="search_filter(this);"
                    value="${filter_domain}"
                    group_by_ctx="${group_context}"
                    title="${help}" />
			</a>
		</li>
	</ul>
</div>

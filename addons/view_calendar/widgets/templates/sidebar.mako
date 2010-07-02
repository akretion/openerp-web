<div id="tertiary">
    <div id="tertiary_wrap">
        <div id="sidebar">
            <div class="sideheader-a">
                <h2>Navigator</h2>
            </div>
            <div id="mini_calendar">
                ${minical.display()}
            </div>
            <div id="group_box">
                ${groupbox.display()}
            </div>
            <div class="sideheader-a">
                <h2>${_('Filter')}</h2>
            </div>
            <ul class="ul_calGroups">
                <li>
                    <input type="checkbox" class="checkbox" id="_terp_use_search" 
                        name="_terp_use_search" onclick="getCalendar()" ${py.checker(use_search)}/>
                    <label for="_terp_use_search">${_("Apply search filter")}</label>
                </li>
            </ul>
        </div>
        <div id="sidebar_hide">
            <a id="toggle-click" class="off" href="javascript: void(0)">
                Toggle
            </a>
            <script type="text/javascript">
                jQuery('#toggle-click').click(function() {
                    toggle_sidebar();
                    CAL_INSTANCE.onResize();
                });
            </script>
        </div>
    </div>
</div>

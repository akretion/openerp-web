<form xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" method="post" id="view_form" name="view_form" action="/form/save">

    <div class="header">

        <div class="title">
            ${screen.string}
        </div>

        <div class="spacer"></div>
                        
<?python 
but_attrs = {}
if screen.view_mode[0] == 'tree': but_attrs['disabled'] = 0
?>

            <div class="toolbar">
            <button type="button" title="Create new record..." onclick="submit_form('new')">New</button>
            <button type="button" title="Save current record..." py:attrs="but_attrs" onclick="submit_form('save')">Save</button>
            <button type="button" title="Remove current record..." onclick="submit_form('delete')" py:attrs="but_attrs">Delete</button>
            <button type="button" title="Previois records..." py:attrs="but_attrs" onclick="submit_form('prev')">Prev</button>
            <button type="button" title="Next records..." py:attrs="but_attrs" onclick="submit_form('next')">Next</button>
            <button type="button" title="Search records..." onclick="submit_form('find')">Find</button>
            <button type="button" title="Switch view..." onclick="submit_form('switch')">Switch</button>
        </div>

    </div>

    <div class="spacer"></div>    
    
    ${screen.display(value_for(screen), **params_for(screen))}
    
</form>
 
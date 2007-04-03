<div xmlns:py="http://purl.org/kid/ns#">
    <table width="100%" border="0" class='fields'>
        <tr py:for="row in table">
            <td py:for="attrs, widget  in row" py:attrs="attrs">
                <span py:if="isinstance(widget, str)" py:replace="widget + ' :'"/>
                <span py:if="not isinstance(widget, str)" py:replace="widget.display(value_for(widget), **params_for(widget))"/>
            </td>
        </tr>
    </table>
</div>
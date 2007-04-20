<!DOCTYPE HTML PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<?python import sitetemplate ?>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="sitetemplate">
<head>
    <meta content="text/html; charset=utf-8" http-equiv="Content-Type" py:replace="''"/>
    <title>Select action</title>
    <link href="/static/css/style.css" rel="stylesheet" type="text/css" />

    <script language="javascript" src="/tg_static/js/MochiKit.js"></script>
    <script language="javascript" src="/static/javascript/master.js"></script>
</head>
<body>

<div class="view">

<script type="text/javascript">
    function onSubmit() {
        var form = $('selection');        
        var result = false;
        
        forEach(form._terp_action, function(e){
            result = result ? result : e.checked;
        });

        return result;
    }
</script>

<form id="selection" action="/selection/action" onsubmit="return onSubmit()">

    <input type="hidden" name="_terp_data" value="${ustr(data)}" />
    
    <div class="header">

        <div class="title">
            Select your action
        </div>
        
        <div class="spacer"></div>
            
            <table width="100%" border="0">
                <tr py:for="key, value in values.items()">
                    <td width="25px"><input type="radio" name="_terp_action" value="${ustr(value)}"/></td>
                    <td py:content="key"></td>
                </tr>
            </table>
           
        <div class="spacer"></div>

        <div class="toolbar">
            <table border="0" cellpadding="0" cellspacing="0" width="100%">
                <tr>
                    <td width="100%">
                    </td>
                    <td>
                        <button type="button" onclick="history.back()">Cancel</button>
                        <button type="submit">OK</button>
                    </td>
                </tr>
            </table>
        </div>

    </div>
</form>    

</div>

</body>
</html>

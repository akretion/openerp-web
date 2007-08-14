<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="tinyerp/templates/master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Database Admin</title>
 </head>
<body>
	<div class="view">
		<div class="box2 welcome">Database Administration</div>
		<div class="box2">
	        <div class="toolbar">
	            <table border="0" cellpadding="0" cellspacing="0" width="100%">
	                <tr>
	                    <td width="100%" align="center">
	                        <button type="button" title="${_('')}" onclick="location.href='/dbadmin/create'">Create</button>
	                        <button type="button" title="${_('')}" onclick="location.href='/dbadmin/drop'">Drop</button>
	                        <button type="button" title="${_('')}" onclick="location.href='/dbadmin/backup'">Backup</button>
	                        <button type="button" title="${_('')}" onclick="location.href='/dbadmin/restore'">Restore</button>
	                        <button type="button" title="${_('')}" onclick="location.href='/dbadmin/password'">Password</button>
	                    </td>
	                </tr>
	            </table>
	        </div>
        </div>
	</div>
</body>
</html>

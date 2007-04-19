<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Login</title>

    <script language="javascript">
    <!--
        function setfocus() {

                var active = document.getElementsByName('host')[0];

                if (document.getElementById("userpwd").style.display == "block") {
                	active = document.getElementsByName('user')[0];
                }

                active.focus();
    	}

		function submitform(){

			var action = "login";

			if (document.getElementById("hostport").style.display == "block") {
				action = "listdb";
			}

			login_action = document.getElementsByName('login_action')[0];
			login_action.value = action;

			document.loginform.submit();
		}

		function checkFrame(){
			if (top.frames.length > 0) {
				content = $("content").innerHTML;
				$("container").innerHTML = "<tr><td valign='top'>" + content + "</td></tr>";
			}
		}
	-->

    </script>
 </head>

<?python
	hostport_style = "none"
	userpwd_style = "block"

	if len(dblist) == 0:
		hostport_style = "block"
		userpwd_style = "none"
?>

<body onload="checkFrame(); setfocus(); return true;">

	<table border="0" cellpadding="5px" cellspacing="0" width="100%" height="100%">
		<tr>
			<td id="content">


		<form action="${targetPage}" method="post" name="loginform">
		<input type="hidden" name="login_action" value="login" />
			<div align="center" class="box" id="hostport" style="display: ${hostport_style}">
				<table align="center" border="0">

					<tr>
						<td align="right" width="90">Host:</td>
						<td><input type="text" name="host" style="width: 100pt;" value="${host}"/></td>
						<td><input type="text" name="port" style="width: 50pt;" value="${port}"/></td>
						<td>
							<input type="submit" name="do_listdb" value="Connect" style="width: 50pt;" onclick="submitform()" />
						</td>
					</tr>
				</table>
			</div>

			<div align="center" id="userpwd" style="display: ${userpwd_style}">
			    	<div class="box">
					<table align="center" border="0" width="100%">
						<tr>
							<td align="right" width="90">Host:</td>
							<td>
								<a href="" onclick="showElement('hostport');hideElement('userpwd');hideElement('message'); document.getElementsByName('host')[0].focus(); return false;">
									${host}:${port}
								</a>
							</td>
						</tr>
					</table>
				</div>

				<div class="box">
					<table align="center" width="100%">
						<tr>
							<td align="right" width="90">Database:</td>
							<td>
								<select name="db" style="width: 100%;">
									<span py:for="db in dblist">
										<option py:content="db" py:if="db == selectedDb" selected="true">dbname</option>
										<option py:content="db" py:if="db != selectedDb">dbname</option>
									</span>
								</select>
							</td>
						</tr>
					</table>
				</div>

				<div class="box">
					<table align="center" width="100%">
						<tr>
							<td align="right" width="90">User:</td>
							<td><input type="text" name="user" id="user" style="width: 99%;" value="${selectedUser}"/></td>
						</tr>
						<tr>
							<td align="right">Password:</td>
							<td><input type="password" name="passwd"  style="width: 99%;"/></td>
						</tr>
						<tr>
							<td>&nbsp;</td>
							<td align="right">
								<input type="submit" name="do_login" value="Log In" onclick="submitform()"/>
							</td>
						</tr>
					</table>
				</div>
				<input type="hidden" py:for="key, value in origArgs.items()" name="${key}" value="${str(value)}"/>
			</div>
		</form>

		<div class="box" style="text-align: center;">
			<a href="/dbadmin">Database Administration</a>
		</div>

		<div class="box message" id="message" py:if="message is not None">
			${message}
		</div>

		</td>
		</tr>
	</table>

</body>

</html>

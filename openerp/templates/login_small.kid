<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:py="http://purl.org/kid/ns#" py:extends="master.kid">

<head>
    <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''"/>
    <title>Login</title>
</head>

<body>
    <div class="view">

        <form action="${target}" method="post" name="loginform">
            <input type="hidden" name="login_action" value="login"/>
        
                <table align="center" cellspacing="2px" border="0">
                    <tr py:if="dblist is not None">
                        <td class="label">
                            <span>Server:</span>
                            <input py:if="dblist is None" type="hidden" name="db" value="$db"/>
                        </td>
                        <td py:content="url"/>
                    </tr>
                    <tr py:if="dblist is not None">
                        <td class="label">Database:</td>
                        <td>
                            <select name="db" style="width: 302px;">
                                <span py:if="dblist and (dblist is not -1)" py:strip="">
                                    <option py:for="v in dblist or []" value="$v" py:content="v" selected="${tg.selector(v==db)}">dbname</option>
                                </span>
                            </select>
                        </td>
                    </tr>

                    <tr>
                        <td class="label">User:</td>
                        <td><input type="text" id="user" name="user" style="width: 150px;" value="${user}"/></td>
                    </tr>
                    
                    <tr>
                        <td class="label">Password:</td>
                        <td><input type="password" value="${password}" id="password" name="password" style="width: 150px;"/></td>
                    </tr>
                    <tr>
                        <td></td>
                        <td align="right">
                            <button type="submit" style="width: 80px; white-space: nowrap">Login</button>
                        </td>
                    </tr>
                </table> 
        </form>

        <div class="box-small message" id="message" py:if="message" py:content="message"/>
    </div>
</body>

</html>


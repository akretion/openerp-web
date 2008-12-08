###############################################################################
#
# Copyright (C) 2007-TODAY Tiny ERP Pvt Ltd. All Rights Reserved.
#
# $Id$
#
# Developed by Tiny (http://openerp.com) and Axelor (http://axelor.com).
#
# The OpenERP web client is distributed under the "OpenERP Public License".
# It's based on Mozilla Public License Version (MPL) 1.1 with following 
# restrictions:
#
# -   All names, links and logos of Tiny, Open ERP and Axelor must be 
#     kept as in original distribution without any changes in all software 
#     screens, especially in start-up page and the software header, even if 
#     the application source code has been changed or updated or code has been 
#     added.
#
# -   All distributions of the software must keep source code with OEPL.
# 
# -   All integrations to any other software must keep source code with OEPL.
#
# If you need commercial licence to remove this kind of restriction please
# contact us.
#
# You can see the MPL licence at: http://www.mozilla.org/MPL/MPL-1.1.html
#
###############################################################################

import re

from turbogears import expose
from turbogears import widgets
from turbogears import controllers
from turbogears import validators, validate
from turbogears import redirect
from turbogears import config

import time

import cherrypy
import pkg_resources

from openerp import rpc
from openerp import common
import xmlrpclib
import base64
from openerp.subcontrollers import actions
from openerp import CONFIG_FILE

conf = config.ConfigObj(CONFIG_FILE, unrepr=True, interpolation=True)

class MySchema(validators.Schema):
    host = validators.String(not_empty=True)
    port = validators.Int(not_empty=True)
    protocol = validators.String(not_empty=True)
    oldpwd = validators.OneOf([conf.get('admin', {}).get('password', '')])
    newpwd = validators.String()
    repwd = validators.String()
    chained_validators = [validators.RequireIfPresent(present='oldpwd',required='newpwd'), validators.FieldsMatch('newpwd', 'repwd')]

class UserPassword(validators.Schema):
    admin_password = validators.String(not_empty=True)
    confirm_password = validators.String(not_empty=True)

class Admin(controllers.Controller):

    @expose(template="openerp.subcontrollers.templates.admin")
    def index(self, message='', id=None, db='', url='', selectedDb='', password=None, admin_password='', confirm_password='', db_name=None, language=[], demo_data=False):
        
        if cherrypy.session.get('auth_check'):
            mode = cherrypy.session.get('auth_check')
        else:
            mode = id
                
        if demo_data:
            demo_data = eval(demo_data)
                                            
        url = rpc.session.get_url()
        url = str(url[:-1])
        
        langlist = []
        dblist = []
        
        try:
            langlist = rpc.session.execute_db('list_lang') or []
        except Exception, e:
            pass
        
        spwd = cherrypy.session.get('terp_password')
        db = cherrypy.request.simple_cookie.get('terp_db')

        try:
            dblist = rpc.session.execute_db('list')
        except:
            pass

        langlist.append(('en_EN','English'))

        host = config.get('host', path="openerp")
        port = config.get('port', path="openerp")
        protocol = config.get('protocol', path="openerp")
        comp_url = config.get('company_url', path='admin')
        
        return dict(langlist=langlist, dbpassword=spwd, dblist=dblist, selectedDb=selectedDb,
                    db=db, url=url, db_name=db_name, demo_data=demo_data,
                    password=password, message=message, mode=mode, host=host,
                    port=port, protocol=protocol, comp_url=comp_url)

    @expose()
    def login(self, **kw):
        
        confpass = conf.get('admin', {}).get('password', '')
        cherrypy.session['auth_check'] = ''
        
        password = kw.get('password')        
        
        if password:
            if password == confpass:
                cherrypy.session['terp_password'] = password
                raise redirect("/admin")
            else:
                message = str(_('Invalid Password...'))
                raise common.error(_('Error'), _(message))
        
        if confpass:
            cherrypy.session['auth_check'] = 'authorize'            
            auth = 'connect_config'
            raise redirect("/admin")
            
        if confpass == "":
            raise common.error(_("Error"), _("Administration password is empty..."))
    
    @validate(validators=MySchema())
    @expose(template="openerp.subcontrollers.templates.admin")
    def setconf(self, new_logo, tg_errors=None, **kw):
        mode = ''
        datas = new_logo.file.read()
        
        if datas:
            try:
                logo_path = pkg_resources.resource_filename("openerp", "static/images/company_logo.png")
                logo_file = open(logo_path, 'wb')
                logo_file.write(datas)
                logo_file.close()
            except Exception, e:
                raise common.error(_('Error'), _('File reading or writing failed...'))
        
        host = kw.get('host')
        port = kw.get('port')
        protocol = kw.get('protocol')
        newpwd = kw.get('newpwd')
        comp_url = kw.get('comp_url')
       
        if comp_url and not comp_url.startswith('http'):
            comp_url = 'http://'+comp_url

        if tg_errors:
            return dict(mode='db_config', message=None, password=None, host=host, port=port, protocol=protocol, comp_url=comp_url)

        oldpwd=kw.get('oldpwd')
        spwd = cherrypy.session.get('terp_password')
        
        if spwd == oldpwd and newpwd:
            cherrypy.session['terp_password'] = newpwd
        
            conf['admin'] = {}
            conf['admin']['password'] = str(newpwd)            
        
        conf['openerp'] = {}
        conf['openerp']['host'] =  str(host)
        conf['openerp']['port'] = str(port)
        conf['openerp']['protocol'] = str(protocol)

        conf['admin']['company_url'] = str(comp_url)
                
        conf.write()

        cherrypy.session['terp_password'] = None

        raise redirect("/admin")
           
    @validate(validators=UserPassword())        
    @expose(template="openerp.subcontrollers.templates.admin")
    def createdb(self, tg_errors=None, langlist=[], password=None, db_name=None, admin_password=None, confirm_password=None, language=[], demo_data=False):
        
        if not db_name:
            return

        message = None
        res = None
        
        langlist = []
        
        try:
            langlist = rpc.session.execute_db('list_lang') or []
        except Exception, e:
            pass

        langlist.append(('en_EN','English'))
    
        if tg_errors:
            return dict(mode='db_create', langlist=langlist, db_name=None, message=None, password=None, admin_password=None, 
                        confirm_password=None, demo_data=False)
        
        if admin_password and (admin_password == confirm_password):
            user_password = admin_password
    
        if ((not db_name) or (not re.match('^[a-zA-Z][a-zA-Z0-9_]+$', db_name))):
            message = _('The database name must contain only normal characters or "_".\nYou must avoid all accents, space or special characters.') + "\n\n" + _('Bad database name!')
        else:
            try:
                res = rpc.session.execute_db('create', password, db_name, demo_data, language, user_password)
        
                time.sleep(5) # wait for few seconds
            except Exception, e:
                if getattr(e, 'faultCode', False) == 'AccessDenied':
                    message = _('Bad database administrator password!') + "\n\n" + _("Could not create database.")
                else:
                    message = _("Could not create database.") + "\n\n" + _('Error during database creation!')
            
            if res:        
                raise redirect("/admin")
            else:
                raise common.error(_('Error'), _(message))
            
    @expose()
    def dropdb(self, db='', dblist=None, db_name=None, password=None):
        
        message=None
        res = None

        if not db_name:
            return
        
        try:
            res = rpc.session.execute_db('drop', password, db_name)
        except Exception, e:
            if getattr(e, 'faultCode', False) == 'AccessDenied':
                message = _('Bad database administrator password!') + "\n\n" + _("Could not drop database.")
            else:
                message = _("Couldn't drop database")

        if res:        
            raise redirect("/admin")
        else:
            raise common.error(_('Error'), _(message))
    
    @expose()
    def backupdb(self, password=None, dblist=None):

        if not dblist:
            return

        message=None
        res = None

        try:
            res = rpc.session.execute_db('dump', password, dblist)
        except Exception, e:
            message = _("Could not create backup.")

        if res:
            cherrypy.response.headers['Content-Type'] = "application/data"
            return base64.decodestring(res)
        else:
            raise common.error(_('Error'), _(message))
        
        raise redirect("/admin")
   
    @expose()
    def restoredb(self, password=None, new_db=None, path=None):

        if path is None:
            return

        message = None
        res = None

        try:
            data_b64 = base64.encodestring(path.file.read())
            res = rpc.session.execute_db('restore', password, new_db, data_b64)
        except Exception, e:
            if getattr(e, 'faultCode', False) == 'AccessDenied':
                message = _('Bad database administrator password!') + "\n\n" + _("Could not restore database.")
            else:
                message = _("Couldn't restore database")

        if res:        
            raise redirect("/admin")
        else:
            raise common.error(_('Error'), _(message))
    
    @expose()
    def passworddb(self, new_password=None, old_password=None, new_password2=None):

        message = None
        res = None

        if not new_password:
            return
        
        if new_password != new_password2:
            message = _("Confirmation password does not match with new password, operation cancelled!") + "\n\n" + _("Validation Error.")
        else:
            try:
                res = rpc.session.execute_db('change_admin_password', old_password, new_password)
            except Exception,e:
                if getattr(e, 'faultCode', False) == 'AccessDenied':
                    message = _("Could not change super admin password.") + "\n\n" + _('Bad password provided!')
                else:
                    message = _("Error, password not changed.")

        if res:        
            raise redirect("/admin")
        else:
            raise common.error(_('Error'), _(message))

# vim: ts=4 sts=4 sw=4 si et


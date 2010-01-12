from openobject.tools import expose

from openerp.controllers import form

from openerp.utils import rpc
from openerp.utils import TinyDict

class ModuleForm(form.Form):
    
    _cp_path = "/modules"
    
    @expose(template="templates/modules.mako")
    def create(self, params, tg_errors=None):
        params.model = "ir.module.web"
        params.view_type = "tree"
        params.view_mode = "['tree']"
        params.ids = None
        params.editable = False
        
        params.context = ctx = rpc.session.context.copy()
        ctx['reload'] = True
        
        form = self.create_form(params, tg_errors)
        return dict(form=form, params=params)
    
    @expose()
    def index(self):
        
        from openobject import addons
        
        modules = addons.get_module_list()
        
        for mod in modules:
            mod.pop("depends", None)
            mod.pop("version", None)
        
        proxy = rpc.RPCProxy("ir.module.web")
        proxy.update_module_list(modules)
        
        params = TinyDict()
        return self.create(params)
    

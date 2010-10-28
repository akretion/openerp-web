import imp
import glob
import os
import py2exe

__all__ = ['opts']

class PackageDataCollector(py2exe.build_exe.py2exe):
    """ Implements collection of package_data in the library file
    generated by py2exe: by default, py2exe takes data_files in
    account, but completely ignores package_data and only bundles the
    pyc (compiled python files) and associated libraries in the
    zipfile.
    """
    def initialize_options(self):
        py2exe.build_exe.py2exe.initialize_options(self)
        self.package_data = None
        self.build_lib = None

    def finalize_options(self):
        self.set_undefined_options('build', ('build_lib', 'build_lib'))
        py2exe.build_exe.py2exe.finalize_options(self)
        self.package_data = self.distribution.package_data

    def package_path(self, package):
        path = None
        for component in package.split('.'):
            _, path, _ = imp.find_module(component, [path] if path else None)
        return path

    def find_data_files(self, package, patterns):
        files = []
        for pattern in patterns:
            files.extend(glob.glob(os.path.normcase(os.path.join(
                self.package_path(package), pattern))))
        return files

    def copy_extensions(self, extensions):
        py2exe.build_exe.py2exe.copy_extensions(self, extensions)
        for package, patterns in self.package_data.iteritems():
            files  = self.find_data_files(package, patterns)
            for f in files:
                f = os.path.relpath(f, self.build_lib)
                dest = os.path.join(self.collect_dir, f)
                self.mkpath(os.path.dirname(dest))
                self.copy_file(
                    os.path.join(self.build_lib, f),
                    dest)
                self.compiled_files.append(f)

opts = {
    'console': ['scripts/openerp-web'],
    'options': {'py2exe': {
        'compressed': 1,
        'optimize': 2,
        'bundle_files': 2,
        'includes': [
            'mako', 'cherrypy', 'babel', 'formencode', 'simplejson', 'csv',
            'dateutil.relativedelta', 'pytz', 'xml.dom.minidom', 'cgitb'
        ],
        'excludes': [
            'Carbon', 'Carbon.Files', 'Crypto', 'DNS', 'OpenSSL', 'Tkinter',
            '_scproxy', 'elementtree.ElementTree', 'email', 'email.Header',
            'email.utils', 'flup.server.fcgi', 'flup.server.scgi',
            'markupsafe._speedups', 'memcache', 'mx', 'pycountry', 'routes',
            'simplejson._speedups', 'turbogears.i18n', 'win32api', 'win32con',
            'win32event', 'win32pipe', 'win32service', 'win32serviceutil'
        ],
        'dll_excludes': [
            'w9xpopen.exe',
        ]
    }},
    'cmdclass': {
        'py2exe': PackageDataCollector
    }
}

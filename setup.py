import os
import sys

from setuptools import setup


execfile(os.path.join("openobject", "release.py"))

if sys.argv[1] == 'bdist_rpm':
    version = version.split('-')[0]


setup(
    name="openerp-web",
    version=version,
    description=description,
    long_description=long_description,
    author=author,
    author_email=email,
    url=url,
    download_url=download_url,
    copyright=copyright,
    license=license,
    install_requires=[
        "CherryPy >= 3.1.2",
        "Mako >= 0.2.4",
        "Babel >= 0.9.4",
        "FormEncode >= 1.2.2",
        "simplejson >= 2.0.9",
        "pyparsing >= 1.5.0"
    ],
    zip_safe=False,
    packages=[
        'openerp-web.scripts',
        'openerp-web.openobject', 
        'openerp-web.addons'],
    package_dir={
        'openerp-web.scripts': 'scripts',
        'openerp-web.openobject': 'openobject',
        'openerp-web.addons': 'addons',
    },
    include_package_data=True,
    data_files = [
        ('openerp-web', ['openerp-web.cfg', 
                         'ChangeLog', 
                         'LICENSE.txt', 
                         'README.txt']),
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Environment :: Web Environment',
        'Topic :: Office/Business :: Financial',
        ],
    scripts=['scripts/openerp-web'],
)

# vim: ts=4 sts=4 sw=4 si et


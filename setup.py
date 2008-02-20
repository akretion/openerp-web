from setuptools import setup, find_packages
from turbogears.finddata import find_package_data

import os
execfile(os.path.join("tinyerp", "release.py"))

packages=find_packages()
package_data = find_package_data(where='tinyerp',
    package='tinyerp')
if os.path.isdir('locales'):
    packages.append('locales')
    package_data.update(find_package_data(where='locales',
        exclude=('*.po',), only_in_packages=False))

setup(
    name="eTiny",
    version=version,

    # uncomment the following lines if you fill them out in release.py
    description='eTiny is the web client of the Tiny ERP, a free enterprise management software: accounting, stock, manufacturing, project mgt...',
    author='Tiny ERP Pvt. Ltd.',
    author_email='info@tinyerp.com',
    url='http://www.tinyerp.com/demonstration.html',
    download_url='http://tinyerp.com/download',
    license='GPL',

    install_requires=[
        "TurboGears >= 1.0.3.2",
    ],
    zip_safe=False,
    packages=packages,
    package_data=package_data,
    keywords=[
        # Use keywords if you'll be adding your package to the
        # Python Cheeseshop

        # if this has widgets, uncomment the next line
        # 'turbogears.widgets',

        # if this has a tg-admin command, uncomment the next line
        # 'turbogears.command',

        # if this has identity providers, uncomment the next line
        # 'turbogears.identity.provider',

        # If this is a template plugin, uncomment the next line
        # 'python.templating.engines',

        # If this is a full application, uncomment the next line
        'turbogears.app',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Framework :: TurboGears',
        # if this is an application that you'll distribute through
        # the Cheeseshop, uncomment the next line
        'Framework :: TurboGears :: Applications',

        # if this is a package that includes widgets that you'll distribute
        # through the Cheeseshop, uncomment the next line
        # 'Framework :: TurboGears :: Widgets',
    ],
    test_suite='nose.collector',
    entry_points = {
        'console_scripts': [
            'start-tinyerp = tinyerp.commands:start',
        ],
    },
    # Uncomment next line and create a default.cfg file in your project dir
    # if you want to package a default configuration in your egg.
    data_files = [('config', ['default.cfg']), 
                  ('scripts', ['etiny-server'])],
    )


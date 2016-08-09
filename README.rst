Deploy readme
=============

The deploy tool is created by Camptocamp with the sponsorship of `Swisstopo <http://geo.admin.ch/>`_.

This tool is used to deploy a geospatial application and related data:

* The Application code with local build.
* The Database.
* The Geospatial files (Geotiff, shapefile, ...).

Usage documentation is printed with `deploy -h`

Development
-----------

The developer environment is set up using:

python -c "import setuptools; execfile('setup.py')" develop

Then it is possible to call bin/deploy.

RPM build
---------

Just execute the two following commands::

    echo "%_unpackaged_files_terminate_build 0" >> ~/.rpmmacros
    python setup.py bdist_rpm --dist-dir ~/ --install-script rpm/install-script

Deploy readme
=============

The deploy tool is created by Camptocamp with the sponsorship of `Swisstopo <http://geo.admin.ch/>`_.

This tool is used do deploy a geospatial application and related data:

* The Application code with local build.
* The Database.
* The Geospatial files (Geotiff, shapefile, ...).

RPM build
---------

Just execute the two following commands::

    echo "%_unpackaged_files_terminate_build 0" >> ~/.rpmmacros
    python setup.py bdist_rpm --dist-dir ~/ --install-script rpm/install-script

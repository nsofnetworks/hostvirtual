HostVirtual
===========

Client library for the HostVirtual API.


Installation
------------

.. code-block:: bash

    $ sudo pip3 install .


Usage
-----

.. code:: python

    # Access HostVirtual Cloud API
    # If api_key is None or not specified, uses HV_API_KEY environment variable
    api_key = 'XXX'
    hvc = HVCloud(api_key)

    # Existing cloud locations, keyed by location's letter code
    locations_dict = hvc.locations()
    # Existing packages
    packages_list = hvc.packages()
    # Available (unassigned) packages
    packages_list = hvc.available_packages()
    # Deployed servers
    servers_list = hvc.servers()

    # Buy a billing package
    pkg_json = hvc.package_buy(plan='VR1x1x25')
    pkg_id = pkg_json['id']
    # Cancel a billing package
    hvc.package_cancel(mbpkgid=pkg_id)

    # Deploy a server
    server_json = hvc.server_build(mbpkgid=pkg_id, fqdn='foo.bar.com',
                                   location='FRA', image='4916',
                                   password='XXXX')
    # Terminate a server
    hvc.server_delete(mbpkgid=pkg_id)

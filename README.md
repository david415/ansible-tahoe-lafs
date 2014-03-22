Role Name
========

Tahoe-lafs - Least Authoratative Filesystem

Here I attempt to use an iterative delopement process which I hope
will result in a flexible and intuitive ansible role for Tahoe-lafs operators.

Specifically we will solve the problem of running Tahoe-lafs using the Tor network...
meaning all our nodes (introducer, storage etc) will be identified with an .onion address.


Role Variables
--------------


Dependencies
------------

future note about requiring torsocks and the ansible-tor role... specifying the hidden server port etc.

Example Playbook
-------------------------

Including an example of how to use your role (for instance, with variables passed in as parameters) is always nice for users too:

    - hosts: tahoe-onion-storage-servers
      roles:
         - { role: david415.tahoe-lafs, }

License
-------

MIT

Feedback, feature requests and bugreports welcome!
--------------------------------------------------

https://github.com/david415


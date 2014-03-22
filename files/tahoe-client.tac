
# -*- python -*-

import pkg_resources
pkg_resources.require('allmydata-tahoe')
pkg_resources.require('twisted')
from allmydata import client
from twisted.application import service

c = client.Client()

application = service.Application("allmydata_client")
c.setServiceParent(application)

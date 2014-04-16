
# -*- python -*-

import pkg_resources
pkg_resources.require('allmydata-tahoe')
pkg_resources.require('twisted')
from allmydata import introducer
from twisted.application import service

c = introducer.IntroducerNode()

application = service.Application("allmydata_introducer")
c.setServiceParent(application)

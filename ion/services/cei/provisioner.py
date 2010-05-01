#!/usr/bin/env python

"""
@file ion/services/cei/provisioner.py
@author Michael Meisinger
@brief service for provisioning new VM instances
"""

import logging
from twisted.internet import defer
from magnet.spawnable import Receiver

import ion.util.procutils as pu
from ion.core.base_process import ProtocolFactory, RpcClient
from ion.services.base_service import BaseService, BaseServiceClient

class ProvisionerService(BaseService):
    """Provisioner service interface
    """

# Spawn of the process using the module name
factory = ProtocolFactory(ProvisionerService)

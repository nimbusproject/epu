#!/usr/bin/env python

from twisted.internet import defer

from magnet.spawnable import spawn

from ion.agents.resource_agent import ResourceAgent
from ion.core.base_process import ProtocolFactory


class InstrumentAgent(ResourceAgent):
    """
    TODO: Add class description
    """

    def op_get(self, content, headers, msg):
        """
        """
        print 'in get'
        print 'headers = ', headers
        print 'content = ', content
        print 'msg = ', msg

    def op_set(self, content, headers, msg):
        """
        """

    def op_getLifecycleState(self, content, headers, msg):
        """
        """

    def op_setLifecycleState(self, content, headers, msg):
        """
        """

    def op_execute(self, content, headers, msg):
        """
        """

    def op_getStatus(self, content, headers, msg):
        """
        """

    def op_getCapabilities(self, content, headers, msg):
        """
        """

# Spawn of the process using the module name
factory = ProtocolFactory(InstrumentAgent)

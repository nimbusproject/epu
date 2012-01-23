class IEpuManagementClient(object):
    """This is a fake interface class that contains the methods any EPU Management client
    implementation will have.  There can be several types of messaging implementations
    that will have different implementations of this client.  And there can be mocks.

    See EPUManagement for parameter documentation.
    """
    def register_need(self, dt_id, constraints, num_needed, subscriber_name, subscriber_op):
        pass

    def retire_node(self, node_id):
        pass

    def subscribe_dt(self, dt_id, subscriber_name, subscriber_op):
        pass

    def unsubscribe_dt(self, dt_id, subscriber_name):
        pass

    def add_epu(self, dt_id, epu_config):
        pass

    def remove_epu(self, dt_id):
        pass

    def reconfigure_epu(self, dt_id, epu_config):
        pass

    def heartbeat(self, content):
        pass

    def instance_info(self, content):
        pass

    def sensor_info(self, content):
        pass


class IProvisionerClient(object):
    """This is a fake interface class that contains the methods any provisioner client
    implementation will have.  There can be several types of messaging implementations
    that will have different implementations of this client.  And there can be mocks.
    """
    def provision(self, launch_id, deployable_type, launch_description, subscribers, vars=None):
        pass

    def terminate_launches(self, launches):
        pass

    def terminate_nodes(self, nodes):
        pass

    def terminate_all(self, rpcwait=False, retries=5, poll=1.0):
        pass

    def dump_state(self, nodes, force_subscribe=None):
        pass

class ISubscriberNotifier(object):
    """This is a fake interface class that contains the methods any subscriber notifier
    implementation will have.  There can be several types of messaging implementations
    that will have different implementations of this client.  And there can be mocks.
    """
    def notify_by_name(self, receiver_name, operation, message):
        """The name is translated into the appropriate messaging-layer object.
        @param receiver_name Message layer name
        @param operation The operation to call on that name
        @param message dict to send
        """
        pass

class IOUAgentClient(object):
    """This is a fake interface class that contains the methods any OU Agent implementation
    will have.  There can be several types of messaging implementations that will have
    different implementations of this client.  And there can be mocks.

    TODO: This belongs in epuagent repository
    """
    def dump_state(self, target_address):
        """Send a heartbeat ASAP.
        """
        pass

    def get_error_info(self, pid, receiver_name):
        """Request the error output from a process, given the ID.
        TODO: Currently this is unused, the heartbeat sends error each message for simplicity.
        """
        pass
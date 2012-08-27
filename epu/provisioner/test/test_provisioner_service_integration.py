import os
import uuid
import tempfile

from socket import timeout
from nose.plugins.skip import SkipTest

try:
    from epuharness.harness import EPUHarness
    from epuharness.fixture import TestFixture
except ImportError:
    raise SkipTest("epuharness not available.")
try:
    from epu.mocklibcloud import MockEC2NodeDriver
except ImportError:
    raise SkipTest("sqlalchemy not available.")

import epu
from epu.dashiproc.dtrs import DTRSClient
from epu.dashiproc.provisioner import ProvisionerClient

default_user = 'default'

fake_libcloud_deployment = """
provisioners:
  prov_0:
    config:
      provisioner:
        default_user: %s
dt_registries:
  dtrs:
    config: {}
"""

fake_credentials = {
  'access_key': 'xxx',
  'secret_key': 'xxx',
  'key_name': 'ooi'
}

dt_name = "sleeper"
sleeper_dt = {
  'mappings': {
    'ec2-fake':{
      'iaas_image': 'ami-fake',
      'iaas_allocation': 't1.micro',
    }
  }
}


class TestProvisionerIntegration(TestFixture):

    def setup(self):

        if not os.environ.get('INT'):
            raise SkipTest("Slow integration test")

        self.exchange = "testexchange-%s" % str(uuid.uuid4())
        self.user = default_user

        self.epuh_persistence = "/tmp/SupD/epuharness"
        if os.path.exists(self.epuh_persistence):
            raise SkipTest("EPUHarness running. Can't run this test")

        epu_path = os.path.dirname(epu.__file__)
        self.dt_data = os.path.join(epu_path, "test", "filedts")
        fh, self.fake_libcloud_db = tempfile.mkstemp()
        os.close(fh)

        deployment = fake_libcloud_deployment % default_user
        self.epuharness = EPUHarness(exchange=self.exchange)
        self.dashi = self.epuharness.dashi

        self.epuharness.start(deployment_str=deployment)

        self.libcloud = MockEC2NodeDriver(sqlite_db=self.fake_libcloud_db)

        self.provisioner_client = ProvisionerClient(self.dashi, topic='prov_0')

        self.fake_site = self.make_fake_libcloud_site()
        self.dtrs_client = DTRSClient(self.dashi, topic='dtrs')

        #wait until provisioner starts
        attempts = 10
        for i in range(0, attempts):
            try:
                self.provisioner_client.describe_nodes()
                break
            except timeout:
                continue
        else:
            assert False, "Wasn't able to talk to provisioner"

        self.load_dtrs()


    def load_dtrs(self):
        self.dtrs_client.add_dt(default_user, dt_name, sleeper_dt)
        self.dtrs_client.add_site(self.fake_site['name'], self.fake_site)
        self.dtrs_client.add_credentials(self.user, self.fake_site['name'], fake_credentials)

    def teardown(self):
        self.epuharness.stop()
        os.remove(self.fake_libcloud_db)

    def test_example(self):

        launch_id = "test"
        instance_ids = ["test"]
        deployable_type = "sleeper"
        site = self.fake_site['name']
        subscribers = []


        self.provisioner_client.provision(launch_id, instance_ids, deployable_type, subscribers, site=site)

        while True:
            instances = self.provisioner_client.describe_nodes()
            if (instances[0]['state'] == '200-REQUESTED' or
                instances[0]['state'] == '400-PENDING'):
                continue
            elif instances[0]['state'] == '600-RUNNING':
                break
            else:
                assert False, "Got unexpected state %s" % instances[0]['state']

        #check that mock has a VM
        mock_vms = self.libcloud.list_nodes()
        assert len(mock_vms) == 1

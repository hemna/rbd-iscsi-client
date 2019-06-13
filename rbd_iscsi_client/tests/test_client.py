# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
"""Tests for `rbd_iscsi_client` package."""


import unittest

from rbd_iscsi_client import client


class TestRbd_iscsi_client(unittest.TestCase):
    """Tests for `rbd_iscsi_client` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        fake_url = 'client://fake-url:0000'
        fake_user = 'user'
        fake_password = 'password'
        self.client = client.RBDISCSIClient(fake_user, fake_password,
                                            fake_url, secure=False,
                                            http_log_debug=True,
                                            suppress_ssl_warnings=False,
                                            timeout=10)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

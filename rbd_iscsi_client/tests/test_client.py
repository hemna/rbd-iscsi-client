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

import mock
import unittest

from rbd_iscsi_client import client


class TestRbd_iscsi_client(unittest.TestCase):
    """Tests for `rbd_iscsi_client` package."""
    FAKE_URL = "http://fake-url:5000"

    RESP_200 = {'status': '200', 'Content-Length': '8787',
                'content-location': u'http://fake-url:5000/api/config',
                'Server': 'Werkzeug/0.14.1 Python/2.7.15rc1',
                'Date': 'Thu, 13 Jun 2019 18:56:46 GMT',
                'Content-Type': 'application/json'}

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
        self.client._http_log_req = mock.Mock()

    def tearDown(self):
        """Tear down test fixtures, if any."""

    @mock.patch.object(client.RBDISCSIClient, '_cs_request')
    def test_get(self, cs_mock):
        """Test something."""
        fake_uri = '/foo'
        body = {}
        cs_mock.return_value = (self.RESP_200, body)
        response, content = self.client.get(fake_uri)
        cs_mock.assert_called_with(fake_uri, 'GET')
        self.assertEqual(response, self.RESP_200)

    @mock.patch.object(client.RBDISCSIClient, '_cs_request')
    def test_put(self, cs_mock):
        """Test something."""
        fake_uri = '/foo'
        body = {}
        cs_mock.return_value = (self.RESP_200, body)
        response, content = self.client.put(fake_uri)
        cs_mock.assert_called_with(fake_uri, 'PUT')
        self.assertEqual(response, self.RESP_200)

    @mock.patch.object(client.RBDISCSIClient, '_cs_request')
    def test_post(self, cs_mock):
        """Test something."""
        fake_uri = '/foo'
        body = {}
        cs_mock.return_value = (self.RESP_200, body)
        response, content = self.client.post(fake_uri)
        cs_mock.assert_called_with(fake_uri, 'POST')
        self.assertEqual(response, self.RESP_200)

    @mock.patch.object(client.RBDISCSIClient, '_cs_request')
    def test_delete(self, cs_mock):
        """Test something."""
        fake_uri = '/foo'
        body = {}
        cs_mock.return_value = (self.RESP_200, body)
        response, content = self.client.delete(fake_uri)
        cs_mock.assert_called_with(fake_uri, 'DELETE')
        self.assertEqual(response, self.RESP_200)

    @mock.patch.object(client.RBDISCSIClient, '_cs_request')
    def test_get_api(self, cs_mock):
        """Test something."""
        fake_uri = '/api'
        body = {}
        cs_mock.return_value = (self.RESP_200, body)
        response, content = self.client.get_api()
        cs_mock.assert_called_with(fake_uri, 'GET')
        self.assertEqual(response, self.RESP_200)

    @mock.patch.object(client.RBDISCSIClient, '_cs_request')
    def test_get_config(self, cs_mock):
        """Test something."""
        fake_uri = '/api/config'
        body = {}
        cs_mock.return_value = (self.RESP_200, body)
        response, content = self.client.get_config()
        cs_mock.assert_called_with(fake_uri, 'GET')
        self.assertEqual(response, self.RESP_200)

    @mock.patch.object(client.RBDISCSIClient, '_cs_request')
    def test_get_gatewayinfo(self, cs_mock):
        """Test something."""
        fake_uri = '/api/gatewayinfo'
        body = {}
        cs_mock.return_value = (self.RESP_200, body)
        response, content = self.client.get_gatewayinfo()
        cs_mock.assert_called_with(fake_uri, 'GET')
        self.assertEqual(response, self.RESP_200)

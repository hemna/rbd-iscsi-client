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
import requests
import unittest

from rbd_iscsi_client import client
from rbd_iscsi_client import exceptions


class TestRbd_iscsi_client(unittest.TestCase):
    """Tests for `rbd_iscsi_client` package."""

    client = None
    FAKE_URL = 'client://fake-url:0000'
    FAKE_USER = 'user'
    FAKE_PASSWORD = 'password'

    def setUp(self):
        self.client = client.RBDISCSIClient(self.FAKE_USER,
                                            self.FAKE_PASSWORD,
                                            self.FAKE_URL,
                                            secure=False,
                                            http_log_debug=True,
                                            suppress_ssl_warnings=False,
                                            timeout=None)

    def tearDown(self):
        self.client = None

    def test_request_timeout(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 10
        retest = mock.Mock()
        http_method = 'fake this'
        http_url = 'http://fake-url:0000'

        with mock.patch('requests.request', retest, create=True):
            # Test timeout exception
            retest.side_effect = requests.exceptions.Timeout
            self.assertRaises(exceptions.Timeout,
                              self.client.request,
                              http_url, http_method)

    def test_request_redirects(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 10
        retest = mock.Mock()
        http_method = 'fake this'
        http_url = 'http://fake-url:0000'

        with mock.patch('requests.request', retest, create=True):
            # Test too many redirects exception
            retest.side_effect = requests.exceptions.TooManyRedirects
            self.assertRaises(exceptions.TooManyRedirects,
                              self.client.request,
                              http_url, http_method)

    def test_request_http_error(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 10
        retest = mock.Mock()
        http_method = 'fake this'
        http_url = 'http://fake-url:0000'

        with mock.patch('requests.request', retest, create=True):
            # Test HTTP Error exception
            retest.side_effect = requests.exceptions.HTTPError
            self.assertRaises(exceptions.HTTPError,
                              self.client.request,
                              http_url, http_method)

    def test_request_url_required(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 10
        retest = mock.Mock()
        http_method = 'fake this'
        http_url = 'http://fake-url:0000'

        with mock.patch('requests.request', retest, create=True):
            # Test URL required exception
            retest.side_effect = requests.exceptions.URLRequired
            self.assertRaises(exceptions.URLRequired,
                              self.client.request,
                              http_url, http_method)

    def test_request_exception(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 10
        retest = mock.Mock()
        http_method = 'fake this'
        http_url = 'http://fake-url:0000'

        with mock.patch('requests.request', retest, create=True):
            # Test request exception
            retest.side_effect = requests.exceptions.RequestException
            self.assertRaises(exceptions.RequestException,
                              self.client.request,
                              http_url, http_method)

    def test_request_ssl_error(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 10
        retest = mock.Mock()

        with mock.patch('requests.request', retest, create=True):
            # Test requests exception
            retest.side_effect = requests.exceptions.SSLError
            self.assertRaisesRegexp(exceptions.SSLCertFailed, "failed")

    def test_client_timeout_setting(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 10
        retest = mock.Mock()

        with mock.patch('requests.request', retest, create=True):
            self.assertEqual(self.client.timeout, 10)

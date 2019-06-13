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

from rbd_iscsi_client import exceptions


class Test_exceptions(unittest.TestCase):
    """Tests for `rbd_iscsi_client` package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_from_response_string_format(self):
        """Test something."""
        class FakeResponse(object):
            status = 500

        fake_response = FakeResponse()
        output = exceptions.from_response(fake_response, {}).__str__()
        self.assertEqual('Internal Server Error (HTTP 500)', output)

    def test_001_client_exception_string_format(self):
        fake_error = {'code': 999,
                      'desc': 'Fake Description',
                      'ref': 'Fake Ref',
                      'debug1': 'Fake Debug 1',
                      'debug2': 'Fake Debug 2', }
        client_ex = exceptions.ClientException(error=fake_error)
        client_ex.message = "Fake Error"
        client_ex.http_status = 500
        output = client_ex.__str__()

        self.assertEqual("Fake Error (HTTP 500) 999 - Fake Description - "
                         "Fake Ref (1: 'Fake Debug 1') (2: 'Fake Debug 2')",
                         output)

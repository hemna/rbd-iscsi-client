#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `rbd_iscsi_client` package."""

import mock
import requests
import unittest

from rbd_iscsi_client import rbd_iscsi_client as client
from rbd_iscsi_client import exceptions


class TestRbd_iscsi_client(unittest.TestCase):
    """Tests for `rbd_iscsi_client` package."""

    client = None

    def setUp(self):
        fake_url = 'client://fake-url:0000'
        fake_user = 'user'
        fake_password = 'password'
        self.client = client.RBDISCSIClient(fake_user, fake_password,
                                            fake_url, secure=False,
                                            http_log_debug=True,
                                            suppress_ssl_warnings=False,
                                            timeout=None,
                                            )

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

    def test_client_retry(self):
        self.client._http_log_req = mock.Mock()
        self.client.timeout = 2
        retest = mock.Mock()
        http_method = 'fake this'
        http_url = 'http://fake-url:0000'

        with mock.patch('requests.request', retest, create=True):
            # Test retry exception
            retest.side_effect = requests.exceptions.ConnectionError
            self.assertRaises(requests.exceptions.ConnectionError,
                              self.client.request,
                              http_url, http_method)

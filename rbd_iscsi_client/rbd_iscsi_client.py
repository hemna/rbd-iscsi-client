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
# under the License."""
""" RBDISCSIClient.

.. module: rbd_iscsi_client

:Author: Walter A. Boring IV
:Description: This is the HTTP REST Client that is used to make calls to
the ceph-iscsi/rbd-target-api service running on the ceph iscsi gateway
host.
"""

import json
import logging
import requests
import time

from rbd_iscsi_client import exceptions


class RBDISCSIClient(object):
    """REST client to rbd-target-api."""

    USER_AGENT = "os_client"

    username = None
    password = None
    api_url = None

    auth = None
    http_log_debug = False
    tries = 5
    delay = 0
    backoff = 2
    timeout = 60

    _logger = logging.getLogger(__name__)
    retry_exceptions = (exceptions.HTTPServiceUnavailable,
                        requests.exceptions.ConnectionError)

    def __init__(self, username, password, base_url,
                 suppress_ssl_warnings=False, timeout=None,
                 secure=False, http_log_debug=False):
        super(RBDISCSIClient, self).__init__()

        self.username = username
        self.password = password
        self.api_url = base_url
        self.timeout = timeout
        self.secure = secure

        self.times = []
        self.set_debug_flag(http_log_debug)

        if suppress_ssl_warnings:
            requests.packages.urllib3.disable_warnings()

        self.auth = requests.auth.HTTPBasicAuth(username, password)

    def set_debug_flag(self, flag):
        """Turn on/off http request/response debugging."""
        if not self.http_log_debug and flag:
            ch = logging.StreamHandler()
            self._logger.setLevel(logging.DEBUG)
            self._logger.addHandler(ch)
            self.http_log_debug = True

    def _http_log_req(self, args, kwargs):
        if not self.http_log_debug:
            return

        string_parts = ['curl -i']
        for element in args:
            if element in ('GET', 'POST'):
                string_parts.append(' -X %s' % element)
            else:
                string_parts.append(' %s' % element)

        for element in kwargs['headers']:
            header = ' -H "%s: %s"' % (element, kwargs['headers'][element])
            string_parts.append(header)

        if 'data' in kwargs:
            string_parts.append(' -d ')
            for key in kwargs['data']:
                string_parts.append('%(key)s=%(value)s&' %
                                    {'key': key,
                                     'value': kwargs['data'][key]})

        self._logger.debug("\nREQ: %s\n" % "".join(string_parts))

    def _http_log_resp(self, resp, body):
        if not self.http_log_debug:
            return
        # Replace commas with newlines to break the debug into new lines,
        # making it easier to read
        self._logger.debug("RESP:%s\n", str(resp).replace("',", "'\n"))
        self._logger.debug("RESP BODY:%s\n", body)

    def request(self, *args, **kwargs):
        """Perform an HTTP Request.

        You should use get, post, delete instead.

        """
        kwargs.setdefault('headers', kwargs.get('headers', {}))
        kwargs['headers']['User-Agent'] = self.USER_AGENT
        kwargs['headers']['Accept'] = 'application/json'
        if 'data' in kwargs:
            payload = kwargs['data']
        else:
            payload = None

        # args[0] contains the URL, args[1] contains the HTTP verb/method
        http_url = args[0]
        http_method = args[1]

        self._http_log_req(args, kwargs)
        r = None
        resp = None
        body = None
        while r is None and self.tries > 0:
            try:
                # Check to see if the request is being retried. If it is, we
                # want to delay.
                if self.delay:
                    time.sleep(self.delay)

                if self.timeout:
                    r = requests.request(http_method, http_url, data=payload,
                                         headers=kwargs['headers'],
                                         auth=self.auth,
                                         verify=self.secure,
                                         timeout=self.timeout)
                else:
                    r = requests.request(http_method, http_url, data=payload,
                                         auth=self.auth,
                                         headers=kwargs['headers'],
                                         verify=self.secure)

                resp = r.headers
                body = r.text
                if isinstance(body, bytes):
                    body = body.decode('utf-8')

                # resp['status'], status['content-location'], and resp.status
                # need to be manually set as Python Requests doesn't provide
                # them automatically.
                resp['status'] = str(r.status_code)
                resp.status = r.status_code
                if 'location' not in resp:
                    resp['content-location'] = r.url

                r.close()
                self._http_log_resp(resp, body)

                # Try and convert the body response to an object
                # This assumes the body of the reply is JSON
                if body:
                    try:
                        body = json.loads(body)
                    except ValueError:
                        pass
                else:
                    body = None

                if resp.status >= 400:
                    if body and 'message' in body:
                        body['desc'] = body['message']

                    raise exceptions.from_response(resp, body)
            except requests.exceptions.SSLError as err:
                self._logger.error(
                    "SSL certificate verification failed: (%s). You must have "
                    "a valid SSL certificate or disable SSL "
                    "verification.", err)
                raise exceptions.SSLCertFailed(
                    "SSL Certificate Verification Failed.")
            except self.retry_exceptions as ex:
                # If we catch an exception where we want to retry, we need to
                # decrement the retry count prepare to try again.
                r = None
                self.tries -= 1
                self.delay = self.delay * self.backoff + 1

                # Raise exception, we have exhausted all retries.
                if self.tries is 0:
                    raise ex
            except requests.exceptions.HTTPError as err:
                raise exceptions.HTTPError("HTTP Error: %s" % err)
            except requests.exceptions.URLRequired as err:
                raise exceptions.URLRequired("URL Required: %s" % err)
            except requests.exceptions.TooManyRedirects as err:
                raise exceptions.TooManyRedirects(
                    "Too Many Redirects: %s" % err)
            except requests.exceptions.Timeout as err:
                raise exceptions.Timeout("Timeout: %s" % err)
            except requests.exceptions.RequestException as err:
                raise exceptions.RequestException(
                    "Request Exception: %s" % err)
        return resp, body

    def _time_request(self, url, method, **kwargs):
        start_time = time.time()
        resp, body = self.request(url, method, **kwargs)
        self.times.append(("%s %s" % (method, url),
                           start_time, time.time()))
        return resp, body

    def _cs_request(self, url, method, **kwargs):
        resp, body = self._time_request(self.api_url + url, method,
                                        **kwargs)
        return resp, body

    def get(self, url, **kwargs):
        return self._cs_request(url, 'GET', **kwargs)

    def post(self, url, **kwargs):
        return self._cs_request(url, 'POST', **kwargs)

    def put(self, url, **kwargs):
        return self._cs_request(url, 'PUT', **kwargs)

    def delete(self, url, **kwargs):
        return self._cs_request(url, 'DELETE', **kwargs)

    def get_api(self):
        """Get the API endpoints."""
        return self.get("/api")

    def get_config(self):
        """Get the complete config object."""
        return self.get("/api/config")

    def get_gatewayinfo(self):
        """Get the number of active sessions on local gateway."""
        return self.get("/api/gatewayinfo")

    def get_targets(self):
        """Get the list of targets defined in the config."""
        api = "/api/targets"
        return self.get(api)

    def create_target_iqn(self, target_iqn, mode=None, controls=None):
        """Create the target iqn on the gateway."""
        api = "/api/target/%(target_iqn)s" % {'target_iqn': target_iqn}
        payload = {}
        if mode:
            payload['mode'] = mode

        if controls:
            payload['controls'] = controls

        return self.put(api, data=payload)

    def delete_target_iqn(self, target_iqn):
        """Delete a target iqn from the gateways."""
        api = "/api/target/%(target_iqn)s" % {'target_iqn': target_iqn}
        return self.delete(api)

    def get_clients(self, target_iqn):
        """List clients defined to the configuration."""
        api = "/api/clients/%(target_iqn)s" % {'target_iqn': target_iqn}
        return self.get(api)

    def get_client_info(self, target_iqn, client_iqn):
        """Fetch the Client information from the gateways.

        Alias, IP address and state for each connected portal.
        """
        api = ("/api/clientinfo/%(target_iqn)s/%(client_iqn)s" %
               {'target_iqn': target_iqn,
                'client_iqn': client_iqn})
        return self.get(api)

    def create_client(self, target_iqn, client_iqn):
        """Delete a client."""
        api = ("/api/client/%(target_iqn)s/%(client_iqn)s" %
               {'target_iqn': target_iqn,
                'client_iqn': client_iqn})
        return self.put(api)

    def delete_client(self, target_iqn, client_iqn):
        """Delete a client."""
        api = ("/api/client/%(target_iqn)s/%(client_iqn)s" %
               {'target_iqn': target_iqn,
                'client_iqn': client_iqn})
        return self.delete(api)

    def set_client_auth(self, target_iqn, client_iqn, username, password):
        """Set the client chap credentials."""
        url = ("/api/clientauth/%(target_iqn)s/%(client_iqn)s" %
               {'target_iqn': target_iqn,
                'client_iqn': client_iqn})
        args = {'username': username,
                'password': password}
        return self.put(url, data=args)

    def get_disks(self):
        """Get the rbd disks defined to the gateways."""
        return self.get("/api/disks")

    def create_disk(self, pool, image, size=None, extras=None):
        """Add a disk to the gateway."""
        url = ("/api/disk/%(pool)s/%(image)s" %
               {'pool': pool,
                'image': image})
        args = {'pool': pool,
                'image': image,
                'mode': 'create'}
        if size:
            args['size'] = size

        if extras:
            args.update(extras)
        return self.put(url, data=args)

    def find_disk(self, pool, image):
        """Find the disk in the gateway."""
        url = ("/api/disk/%(pool)s/%(image)s" %
               {'pool': pool,
                'image': image})
        return self.get(url)

    def delete_disk(self, pool, image):
        """delete a disk from the gateway."""
        url = ("/api/disk/%(pool)s/%(image)s" %
               {'pool': pool,
                'image': image})
        return self.delete(url)

    def register_disk(self, target_iqn, volume):
        """Add the volume to the target definition.

        This is done after the disk is created in a pool, and
        before the disk can be exported to an initiator.
        """
        url = ("/api/targetlun/%(target_iqn)s" %
               {'target_iqn': target_iqn})
        args = {'disk': volume}
        return self.put(url, data=args)

    def unregister_disk(self, target_iqn, volume):
        """Remove the volume from the target definition.

        This is done after the disk is unexported from an initiator
        and before the disk can be deleted from the gateway.
        """
        url = ("/api/targetlun/%(target_iqn)s" %
               {'target_iqn': target_iqn})
        args = {'disk': volume}
        return self.delete(url, data=args)

    def export_disk(self, target_iqn, client_iqn, pool, disk):
        """Add a disk to export to a client."""
        url = ("/api/clientlun/%(target_iqn)s/%(client_iqn)s" %
               {'target_iqn': target_iqn,
                'client_iqn': client_iqn})
        args = {'disk': "%(pool)s/%(disk)s" % {'pool': pool, 'disk': disk},
                'client_iqn': client_iqn}
        return self.put(url, data=args)

    def unexport_disk(self, target_iqn, client_iqn, pool, disk):
        """Remove a disk to export to a client."""
        url = ("/api/clientlun/%(target_iqn)s/%(client_iqn)s" %
               {'target_iqn': target_iqn,
                'client_iqn': client_iqn})
        args = {'disk': "%(pool)s/%(disk)s" % {'pool': pool, 'disk': disk}}
        return self.delete(url, data=args)

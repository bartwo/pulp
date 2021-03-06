# -*- coding: utf-8 -*-
#
# Copyright © 2013 Red Hat, Inc.
#
# This software is licensed to you under the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the License
# (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied, including the
# implied warranties of MERCHANTABILITY, NON-INFRINGEMENT, or FITNESS FOR A
# PARTICULAR PURPOSE.
# You should have received a copy of GPLv2 along with this software; if not,
# see http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt

import os
import unittest
from cStringIO import StringIO

from pulp.common.download.config import DownloaderConfig
from pulp.common.download.downloaders import event as eventlet_downloader

from http_static_test_server import HTTPStaticTestServer
from test_common_download import DownloadTests, MockEventListener

# evenetlet downloader tests ---------------------------------------------------

class EventletDownloaderInstantiationTests(unittest.TestCase):

    def test_instantiation(self):
        config =  DownloaderConfig()
        try:
            eventlet_downloader.HTTPEventletDownloader(config)
        except Exception, e:
            self.fail(str(e))


class LiveEventletDownloaderTests(DownloadTests):

    http_server = None

    @classmethod
    def setUpClass(cls):
        cls.http_server = HTTPStaticTestServer()
        cls.http_server.start()

    @classmethod
    def tearDownClass(cls):
        cls.http_server.stop()
        cls.http_server = None

    def test_download_single(self):
        config = DownloaderConfig()
        downloader = eventlet_downloader.HTTPEventletDownloader(config)
        request_list = self._download_requests()[:1]
        downloader.download(request_list)

        input_file_name = self.file_list[0]
        input_file_size = self.file_sizes[0]

        output_file_path = os.path.join(self.storage_dir, input_file_name)
        output_file_size = os.path.getsize(output_file_path)

        self.assertEqual(input_file_size, output_file_size)

    def test_download_multiple(self):
        downloader = eventlet_downloader.HTTPEventletDownloader(DownloaderConfig())
        request_list = self._download_requests()

        try:
            downloader.download(request_list)

        except Exception, e:
            self.fail(str(e))

    def test_file_like_destination(self):
        downloader = eventlet_downloader.HTTPEventletDownloader(DownloaderConfig())
        request_list = self._download_requests()[:1]
        request_list[0].destination = StringIO()
        downloader.download(request_list)

        contents = request_list[0].destination.getvalue()

        self.assertEqual(len(contents), self.file_sizes[0])

        try:
            request_list[0].destination.close()
        except Exception, e:
            self.fail(str(e))

    def test_download_event_listener(self):
        listener = MockEventListener()
        downloader = eventlet_downloader.HTTPEventletDownloader(DownloaderConfig(), listener)
        request_list = self._download_requests()[:1]
        downloader.download(request_list)

        self.assertEqual(listener.download_started.call_count, 1)
        self.assertNotEqual(listener.download_progress.call_count, 0) # not sure how many times
        self.assertEqual(listener.download_succeeded.call_count, 1)
        self.assertEqual(listener.download_failed.call_count, 0)

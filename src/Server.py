#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 14:53:00 2020

@author: fatih
"""

import json
import tarfile
from hashlib import md5
from pathlib import Path
from shutil import rmtree

import gi

gi.require_version("GLib", "2.0")
gi.require_version("Soup", "2.4")
from gi.repository import GLib, Gio


class Server(object):
    def __init__(self):
        pass

    def get(self, url, type):
        file = Gio.File.new_for_uri(url)
        file.load_contents_async(None, self._open_stream, type)

    def _open_stream(self, file, result, type):
        try:
            success, data, etag = file.load_contents_finish(result)
        except GLib.Error as error:
            self.error_message = error.message
            print(
                "{} _open_stream Error: {}, {}".format(
                    type, error.domain, error.message
                )
            )
            self.ServerGet(response=None)  # Send to MainWindow
            return False

        if success:
            self.ServerGet(json.loads(data))
        else:
            print("{} is not success".format(type))
            self.ServerGet(response=None)  # Send to MainWindow

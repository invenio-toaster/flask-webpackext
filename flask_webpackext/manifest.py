# -*- coding: utf-8 -*-
#
# This file is part of Flask-WebpackExt
# Copyright (C) 2017 CERN.
#
# Flask-WebpackExt is free software; you can redistribute it and/or modify
# it under the terms of the Revised BSD License; see LICENSE file for
# more details.

"""Proxy to current extension."""

from __future__ import absolute_import, print_function

from flask import current_app
from markupsafe import Markup
from pywebpack import Manifest, ManifestEntry, ManifestLoader

from .errors import ManifestKeyNotFoundError


class JinjaManifest(Manifest):
    """Manifest entry which marks rendered strings as safe for Jinja."""

    def __getitem__(self, key):
        """Get a manifest entry."""
        try:
            return super(JinjaManifest, self).__getitem__(key)
        except KeyError:
            raise ManifestKeyNotFoundError('Key {} not found in manifest.json'
                                           .format(key))

    def __getattr__(self, name):
        """Get a manifest entry."""
        try:
            return super(JinjaManifest, self).__getattr__(name)
        except AttributeError as e:
            raise ManifestKeyNotFoundError('Key {} not found in manifest.json'
                                           .format(name))


class JinjaManifestEntry(ManifestEntry):
    """Manifest entry which marks rendered strings as safe for Jinja."""

    def __html__(self):
        """Ensures that string is not escaped when included in Jinja."""
        return Markup(self.render())


class JinjaManifestLoader(ManifestLoader):
    """Factory which uses the Jinja manifest entry."""

    cache = {}

    def __init__(self, manifest_cls=JinjaManifest,
                 entry_cls=JinjaManifestEntry):
        """Initialize manifest loader."""
        super(JinjaManifestLoader, self).__init__(
            manifest_cls=manifest_cls,
            entry_cls=entry_cls
        )

    def load(self, filepath):
        """Load a manifest from a file."""
        if current_app.debug or filepath not in JinjaManifestLoader.cache:
            JinjaManifestLoader.cache[filepath] = \
                super(JinjaManifestLoader, self).load(filepath)
        return JinjaManifestLoader.cache[filepath]

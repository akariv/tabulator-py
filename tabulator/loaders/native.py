# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from . import api


# Module API

class NativeLoader(api.Loader):
    """Null loader to pass python native lists.
    """

    # Public

    options = []

    def load(self, source, encoding, mode):
        pass

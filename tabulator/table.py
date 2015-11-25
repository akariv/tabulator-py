# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import namedtuple


class Table(object):
    """Table representation.

    Args:
        loader (tabulator.loaders.API): table loader
        parser (tabulator.parsers.API): table parser

    """

    # Public

    def __init__(self, loader, parser):
        self.__loader = loader
        self.__parser = parser
        self.__processors = []
        self.__bytes = None
        self.__items = None
        self.__headers = None

    def __enter__(self):
        """Enter context manager by opening table.
        """
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        """Exit context manager by closing table.
        """
        self.close()

    def add_processor(self, processor):
        """Add processor to pipeline.
        """
        self.__processors.append(processor)

    def open(self):
        """Open table by opening source stream.
        """
        if self.closed:
            self.__bytes = self.__loader.load()
            self.__items = self.__parser.parse(self.__bytes)

    def reset(self):
        """Reset pointer to the first row.
        """
        self.__bytes.seek(0)

    def close(self):
        """Close table by closing source stream.
        """
        if self.__bytes:
            self.__bytes.close()

    @property
    def closed(self):
        """Return true if table is closed.
        """
        return not self.__bytes or self.__bytes.closed

    @property
    def headers(self):
        """Return table headers.
        """
        if self.__headers is None:
            if self.__bytes.tell() == 0:
                for _, _, _ in self.__iterate():
                    if self.__headers is not None:
                        break
                self.__bytes.seek(0)
        return self.__headers

    def readrow(self, with_headers=False):
        """Return next row from the source stream.
        """
        for index, headers, values in self.__iterate():
            row = values
            if with_headers:
                if headers is None:
                    raise RuntimeError('No headers are available.')
                Row = namedtuple('Row', headers)
                row = Row(*values)
            yield row

    def read(self, with_headers=False, limit=None):
        """Return full table.
        """
        rows = []
        rows_iter = self.readrow(with_headers=with_headers)
        for index, row in enumerate(rows_iter):
            if index > limit:
                break
            rows.append(row)
        return rows

    # Private

    def __iterate(self):
        if self.closed:
            message = (
               'Table have to be opened by `table.open()` before '
               'iteration interface will be available.')
            raise RuntimeError(message)
        index = None
        headers = None
        for keys, values in self.__items:
            if keys is not None:
                headers = keys
            if index is None:
                index = 1
            else:
                index += 1
            for processor in self.__processors:
                if index is None:
                    self.__bytes.seek(0)
                    break
                if values is None:
                    break
                index, headers, values = processor.process(
                        index, headers, values)
            if headers is not None:
                self.__headers = headers
            if values is not None:
                yield (index, headers, values)
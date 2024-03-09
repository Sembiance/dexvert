"""
:mod:`pyffi.formats.dae` --- COLLADA (.dae)
===========================================

.. warning::
   
   This module is not yet fully implemented, and is certainly not
   yet useful in its current state.

Implementation
--------------

.. autoclass:: DaeFormat
   :show-inheritance:
   :members:

Regression tests
----------------

Create a DAE file
^^^^^^^^^^^^^^^^^

>>> daedata = DaeFormat.Data()
>>> print(daedata.collada) # doctest: +ELLIPSIS
<...Collada object at ...>

Read a DAE file
^^^^^^^^^^^^^^^
>>> from os.path import dirname
>>> dirpath = __file__
>>> for i in range(4): #recurse up to root repo dir
...     dirpath = dirname(dirpath)
>>> repo_root = dirpath
>>> format_root = os.path.join(repo_root, 'tests', 'formats', 'dae')
>>> # check and read dae file
>>> stream = open(os.path.join(format_root, 'cube.dae'), 'rb')
>>> daedata = DaeFormat.Data()
>>> daedata.read(stream) # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
NotImplementedError
>>> # get DAE file root element
>>> #print(daedata.getRootElement())
>>> stream.close()

Parse all DAE files in a directory tree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> for stream, data in DaeFormat.walkData(format_root):
...     try:
...         # the replace call makes the doctest also pass on windows
...         os_path = stream.name
...         split = (os_path.split(os.sep))[-4:]
...         rejoin = os.path.join(*split).replace(os.sep, "/")
...         print("reading %s" % rejoin)
...         data.read(stream)
...     except Exception:
...         print("Warning: read failed due corrupt file, corrupt format description, or bug.")
reading tests/formats/dae/cube.dae
Warning: read failed due corrupt file, corrupt format description, or bug.

Create a DAE file from scratch and write to file
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

>>> daedata = DaeFormat.Data()
>>> from tempfile import TemporaryFile
>>> stream = TemporaryFile()
>>> daedata.write(stream) # doctest: +ELLIPSIS
Traceback (most recent call last):
    ...
NotImplementedError
"""

# ***** BEGIN LICENSE BLOCK *****
#
# Copyright (c) 2007-2012, Python File Format Interface
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above
#      copyright notice, this list of conditions and the following
#      disclaimer in the documentation and/or other materials provided
#      with the distribution.
#
#    * Neither the name of the Python File Format Interface
#      project nor the names of its contributors may be used to endorse
#      or promote products derived from this software without specific
#      prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# ***** END LICENSE BLOCK *****

import struct
import os
import re

import pyffi.object_models.xsd

class DaeFormat(pyffi.object_models.xsd.FileFormat):
    """This class implements the DAE format."""
    xsdFileName = 'COLLADASchema.xsd'
    # where to look for the xsd file and in what order:
    # DAEXSDPATH env var, or XsdFormat module directory
    xsdFilePath = [os.getenv('DAEXSDPATH'), os.path.dirname(__file__)]
    # file name regular expression match
    RE_FILENAME = re.compile(r'^.*\.dae$', re.IGNORECASE)
    # used for comparing floats
    _EPSILON = 0.0001

    class Data(pyffi.object_models.xsd.FileFormat.Data):
        """A class to contain the actual collada data."""

        def __init__(self, version=0x01040100):
            """Initialize collada data. By default, this creates an
            empty collada 1.4.1 root element.

            :param version: The collada version (for instance, 0x01040100 for
                1.4.1).
            :type version: int
            """
            # TODO integrate the Collada and Data elements
            self.collada = DaeFormat.Collada()

        def getVersion(self):
            """Get the collada version, as integer (for instance, 1.4.1 would be
            0x01040100).

            :return: The version, as integer.
            """
            return 0x01040100

        # overriding pyffi.object_models.FileFormat.Data methods

        def inspect(self, stream):
            """Quickly checks whether the stream appears to contain
            collada data. Resets stream to original position. If the stream
            turns out to be collada, L{getVersion} is guaranteed to return
            the version.

            Call this function if you simply wish to check that a file is
            a collada file without having to parse it completely.

            :param stream: The file to inspect.
            :type stream: file
            :return: ``True`` if stream is collada, ``False`` otherwise.
            """
            raise NotImplementedError

        def read(self, stream):
            """Read collada data from stream.

            :param stream: The file to read from.
            :type stream: file
            """
            raise NotImplementedError

        def write(self, stream):
            """Write collada data to stream.

            :param stream: The file to write to.
            :type stream: file
            """
            raise NotImplementedError

    # basic types
    # TODO

    # implementation of dae-specific basic types
    # TODO


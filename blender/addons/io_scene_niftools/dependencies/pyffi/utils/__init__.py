"""This module bundles various general purpose utilities:
- hexdumping
- parsing all files in a directory tree
- 3D related tasks (see TriStrip.py, MathUtils.py, QuickHull.py, and Inertia.py)
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

import os
from distutils.cmd import Command


class BuildDoc(Command): # pragma: no cover
    """
    Distutils command to stop setup.py from throwing errors
    if sphinx is not installed
    """
    
    description = 'Sphinx is not installed'
    user_options = []
    
    def initialize_options(self):
        self.source_dir = self.build_dir = None
        self.project = ''
        self.version = ''
        self.release = ''
    
    def finalize_options(self):
        return

    def run(self):
        raise ModuleNotFoundError("Sphinx is not installed")


def walk(top, topdown=True, onerror=None, re_filename=None):
    """A variant of os.walk() which also works if top is a file instead of a
    directory, filters files by name, and returns full path. File names are
    returned in alphabetical order.

    :param top: The top directory or file.
    :type top: str
    :param topdown: Whether to list directories first or not.
    :type topdown: bool
    :param onerror: Which function to call when an error occurs.
    :type onerror: function
    :param re_filename: Regular expression to match file names.
    :type re_filename: compiled regular expression (see re module)
    """
    if os.path.isfile(top):
        dirpath, filename = os.path.split(top)
        if re_filename:
            if re_filename.match(filename):
                yield top
        else:
            yield top
    else:
        for dirpath, dirnames, filenames in os.walk(top):
            filenames = sorted(filenames)
            for filename in filenames:
                if re_filename:
                    if re_filename.match(filename):
                        yield os.path.join(dirpath, filename)
                else:
                    yield os.path.join(dirpath, filename)


# table = "."*32
# for c in [chr(i) for i in range(32,128)]:
#     table += c
# table += "."*128
chartable = '................................ !"#$%&\'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[\\]^_`abcdefghijklmnopqrstuvwxyz{|}~.................................................................................................................................'.encode("ascii")


def hex_dump(f, num_lines=8):
    """A function for hexdumping."""

    dumpstr = ""

    pos = f.tell()
    if pos > num_lines*8:
        f.seek((pos-num_lines*8) & 0xfffffff0)
    else:
        f.seek(0)
    dumppos = f.tell()
    dumpstr += "            "
    for ofs in range(16):
        dumpstr += "%02X " % ofs
    dumpstr += "\n-----------------------------------------------------------\n"
    for i in range(num_lines):
        dumpstr += "0x%08X " % dumppos
        data = f.read(16)
        for j, c in enumerate(data):
            # py3k: data is bytes object, so c is int already
            # py2x: data is string, so convert c to int with ord
            if isinstance(c, int):
                cc = c
            else:
                cc = ord(c)
            if dumppos + j != pos:
                dumpstr += " %02X" % cc
            else:
                dumpstr += ">%02X" % cc
        for j in range(len(data), 16):
            dumpstr += "   "
            data += " ".encode("ascii")
        dumpstr += " |" + data.translate(chartable).decode("ascii") + "|\n"
        dumppos += 16
    return dumpstr


def unique_map(hash_generator):
    """Return a map and inverse map to identify unique values based
    on hash, which is useful for removing duplicate data. If the hash
    generator yields None then the value is mapped to None (useful for
    discarding data).
    """

    hash_map = []  # maps old index to new index
    hash_map_inverse = []  # inverse: map new index to old index
    hash_index_map = {None: None}  # maps hash to new index (default for None)
    new_index = 0
    for old_index, hash_ in enumerate(hash_generator):
        try:
            hash_index = hash_index_map[hash_]
        except KeyError:
            # hash is new
            hash_index_map[hash_] = new_index
            hash_map.append(new_index)
            hash_map_inverse.append(old_index)
            new_index += 1
        else:
            # hash already exists
            hash_map.append(hash_index)
    return hash_map, hash_map_inverse


if __name__ == '__main__':
    import doctest
    doctest.testmod()

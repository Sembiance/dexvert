# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Ps2sys(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic_string = self._io.ensure_fixed_contents(b"\x50\x53\x32\x44")
        self.reserved1 = self._io.ensure_fixed_contents(b"\x00\x00")
        self.offset_2nd_line = self._io.read_u2le()
        self.reserved2 = self._io.ensure_fixed_contents(b"\x00\x00\x00\x00")
        self.bg_opacity = self._io.read_u4le()
        self.bg_color_upperleft = self._root.BgColor(self._io, self, self._root)
        self.bg_color_upperright = self._root.BgColor(self._io, self, self._root)
        self.bg_color_lowerleft = self._root.BgColor(self._io, self, self._root)
        self.bg_color_lowerright = self._root.BgColor(self._io, self, self._root)
        self.light1_direction = self._root.LightDirection(self._io, self, self._root)
        self.light2_direction = self._root.LightDirection(self._io, self, self._root)
        self.light3_direction = self._root.LightDirection(self._io, self, self._root)
        self.light1_color = self._root.LightColor(self._io, self, self._root)
        self.light2_color = self._root.LightColor(self._io, self, self._root)
        self.light3_color = self._root.LightColor(self._io, self, self._root)
        self.light_ambient_color = self._root.LightColor(self._io, self, self._root)
        self.title = (self._io.read_bytes(68)).decode(u"Shift_JIS")
        self.icon_file = (self._io.read_bytes(64)).decode(u"ASCII")
        self.icon_copy_file = (self._io.read_bytes(64)).decode(u"ASCII")
        self.icon_delete_file = (self._io.read_bytes(64)).decode(u"ASCII")
        self.reserved3 = self._io.read_bytes(512)

    class BgColor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.r = self._io.read_u4le()
            self.g = self._io.read_u4le()
            self.b = self._io.read_u4le()
            self.a = self._io.read_u4le()


    class LightDirection(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_f4le()
            self.y = self._io.read_f4le()
            self.z = self._io.read_f4le()
            self.w = self._io.read_f4le()


    class LightColor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.r = self._io.read_f4le()
            self.g = self._io.read_f4le()
            self.b = self._io.read_f4le()
            self.a = self._io.read_f4le()




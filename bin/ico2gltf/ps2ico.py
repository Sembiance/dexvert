# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

from pkg_resources import parse_version
from kaitaistruct import __version__ as ks_version, KaitaiStruct, KaitaiStream, BytesIO


if parse_version(ks_version) < parse_version('0.7'):
    raise Exception("Incompatible Kaitai Struct Python API: 0.7 or later is required, but you have %s" % (ks_version))

class Ps2ico(KaitaiStruct):
    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.file_id = self._io.ensure_fixed_contents(b"\x00\x00\x01\x00")
        self.animation_shapes = self._io.read_u4le()
        self.texture_type = self._io.read_u4le()
        self.reserved = self._io.read_u4le()
        self.vertex_count = self._io.read_u4le()
        self.vertices = [None] * (self.vertex_count)
        for i in range(self.vertex_count):
            self.vertices[i] = self._root.VertexInfo(self._io, self, self._root)

        self.tag_id = self._io.read_u4le()
        self.frame_length = self._io.read_u4le()
        self.animation_speed = self._io.read_f4le()
        self.play_offset = self._io.read_u4le()
        self.frame_count = self._io.read_u4le()
        self.frames = [None] * (self.frame_count)
        for i in range(self.frame_count):
            self.frames[i] = self._root.FrameInfo(self._io, self, self._root)

        _on = self.texture_type
        if _on == 15:
            self.texture = self._root.CompressedTexture(self._io, self, self._root)
        else:
            self.texture = self._root.UncompressedTexture(self._io, self, self._root)

    class CompressedTexture(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.size = self._io.read_u4le()
            self.data = [None] * (self.size // 2)
            for i in range(self.size // 2):
                self.data[i] = self._io.read_u2le()



    class VertexCoord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.x = self._io.read_s2le()
            self.y = self._io.read_s2le()
            self.z = self._io.read_s2le()
            self.unknown = self._io.read_s2le()


    class UncompressedTexture(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.data = [None] * ((128 * 128))
            for i in range((128 * 128)):
                self.data[i] = self._io.read_u2le()



    class TexCoord(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.u = self._io.read_s2le()
            self.v = self._io.read_s2le()


    class FrameInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.shape_id = self._io.read_u4le()
            self.key_count = self._io.read_u4le()
            self.keys = [None] * (self.key_count)
            for i in range(self.key_count):
                self.keys[i] = self._root.FrameKey(self._io, self, self._root)



    class FrameKey(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.time = self._io.read_f4le()
            self.value = self._io.read_f4le()


    class VertexColor(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.r = self._io.read_u1()
            self.g = self._io.read_u1()
            self.b = self._io.read_u1()
            self.a = self._io.read_u1()


    class VertexInfo(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.positions = [None] * (self._parent.animation_shapes)
            for i in range(self._parent.animation_shapes):
                self.positions[i] = self._root.VertexCoord(self._io, self, self._root)

            self.normal = self._root.VertexCoord(self._io, self, self._root)
            self.tex_coord = self._root.TexCoord(self._io, self, self._root)
            self.color = self._root.VertexColor(self._io, self, self._root)




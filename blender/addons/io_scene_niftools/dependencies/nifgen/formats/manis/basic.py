import logging
from struct import Struct

from nifgen.array import Array
from nifgen.formats.base.basic import Uint, Ushort, Ubyte, Int64


class ChannelName:

    def __new__(cls, context=None, arg=0, template=None):
        return ""

    @staticmethod
    def cls_from_context(context):
        # if context.version <= 236:
        #     return Ubyte
        if context.version <= 257:
            return Ushort
        else:
            return Uint

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        ind = cls.cls_from_context(context).from_stream(stream, context, arg, template)
        try:
            return context.name_buffer.bone_names[ind]
        except (IndexError, ValueError):
            raise IndexError(f"Index '{ind}' exceeds names list '{context.name_buffer.bone_names}' at offset {stream.tell()}")

    @classmethod
    def to_stream(cls, instance, stream, context, arg=0, template=None):
        # bones list needs to be filled before writing
        # now we just take the index prepared by the string table
        try:
            ind = context.name_buffer.bone_names.index(instance)
        except (IndexError, ValueError):
            raise IndexError(f"String '{instance}' was missing from names list '{context.name_buffer.bone_names}'")
        # print(offset, instance, arg.offset_dic)
        cls.cls_from_context(context).to_stream(ind, stream, context, arg, template)

    @staticmethod
    def fmt_member(member, indent=0):
        return str(member)


class BoneIndex(Ubyte):

    def __new__(cls, context=None, arg=0, template=None):
        return ""

    @staticmethod
    def cls_from_arg(arg):
        if arg.use_ushort:
            return Ushort
        else:
            return Ubyte

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        return cls.cls_from_arg(arg).from_stream(stream, context, arg, template)

    @classmethod
    def to_stream(cls, instance, stream, context, arg=0, template=None):
        cls.cls_from_arg(arg).to_stream(instance, stream, context, arg, template)

    @staticmethod
    def fmt_member(member, indent=0):
        return str(member)


class Int48(Int64):
    mask = 0b111111111111111111111111111111111111111111111111

    def __new__(cls, context=None, arg=0, template=None):
        return 0

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        c = stream.tell()
        ind = super().from_stream(stream, context, arg, template)
        stream.seek(c+6)
        return ind & cls.mask

    @classmethod
    def to_stream(cls, instance, stream, context, arg=0, template=None):
        ind = instance & cls.mask
        c = stream.tell()
        super().to_stream(ind, stream, context, arg, template)
        stream.seek(c+6)

    @staticmethod
    def fmt_member(member, indent=0):
        return str(member)


import numpy as np

from nifgen.formats.base.basic import Uint, Int, Ubyte, Ushort


class BiosynVersion(Uint):

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        value = super().from_stream(stream, context, arg, template)
        context.biosyn = value
        return value


class MainVersion(Uint):

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        value = super().from_stream(stream, context, arg, template)
        context.version = value
        return value


class BonePointerIndex(Uint):

    def __new__(cls, context=None, arg=0, template=None):
        return ""

    @staticmethod
    def cls_from_context(context):
        if context.version < 53:
            return Ubyte
        else:
            return Ushort

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        return cls.cls_from_context(context).from_stream(stream, context, arg, template)

    @classmethod
    def to_stream(cls, instance, stream, context, arg=0, template=None):
        # print(offset, instance, arg.offset_dic)
        trg_cls = cls.cls_from_context(context)
        instance = min(instance, np.iinfo(trg_cls.np_dtype).max)
        trg_cls.to_stream(instance, stream, context, arg, template)


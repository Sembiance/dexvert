import logging
from struct import Struct

from nifgen.array import Array
from nifgen.formats.base.basic import class_from_struct, ZString, r_zstr, w_zstr, Int

Bool = class_from_struct(Struct("<?"), bool)


separator = "::"


def r_zstr_obfuscated(r_func):
    _hash, _name = r_zstr(r_func).split(separator)
    name_str = _obfuscate(_name, delta=-1)
    return f"{_hash}{separator}{name_str}"


def w_zstr_obfuscated(w_func, s):
    _hash, _name = s.split(separator)
    name_str = _obfuscate(_name, delta=+1)
    w_zstr(w_func, f"{_hash}{separator}{name_str}")


def _obfuscate(s, delta=1):
    b = bytearray(s.encode())
    # decode the names
    for i in range(len(b)):
        b[i] = max(0, b[i] + delta)
    return b.decode()


class ZStringObfuscated(ZString):

    @staticmethod
    def from_stream(stream, context=None, arg=0, template=None):
        return r_zstr_obfuscated(stream.read)

    @staticmethod
    def to_stream(instance, stream, context=None, arg=0, template=None):
        w_zstr_obfuscated(stream.write, instance)

    @staticmethod
    def fmt_member(member, indent=0):
        lines = str(member).split("\n")
        lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
        return "\n".join(lines_new)


class OffsetString(Int):

    @classmethod
    def from_stream(cls, stream, context, arg=0, template=None):
        offset = super().from_stream(stream, context, arg, template)
        # arg must be ZStringBuffer
        try:
            return arg.get_str_at(offset)
        except:
            return ""

    @classmethod
    def to_stream(cls, instance, stream, context, arg=0, template=None):
        # logging.info(f"arg {instance}, {arg}")
        # arg = ZStringBuffer needs to be filled before writing
        # now we just take the index prepared by the string table
        try:
            offset = arg.offset_dic.get(instance)
        except KeyError:
            raise KeyError(f"String '{instance}' was missing from ZStringBuffer '{arg}'")
        # print(offset, instance, arg.offset_dic)
        super().to_stream(offset, stream, context, arg, template)

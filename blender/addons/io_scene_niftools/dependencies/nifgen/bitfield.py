import logging
from nifgen.base_struct import StructMetaClass


class BitfieldMetaClass(StructMetaClass):

    def __init__(cls, name, bases, dict, **kwds):
        total_members = []
        for key, value in dict.items():
            if isinstance(value, BitfieldMember):
                total_members.append(key)
        cls.__members__ = total_members

class BitfieldMember(object):

    def __init__(self, pos=0, width=0, mask=0, return_type=bool):
        self.pos = pos
        self.mask = mask
        self.width = width
        self.return_type = return_type

    # see https://github.com/niftools/nifxml/issues/76 for reference
    def __get__(self, instance, owner):
        return self.return_type((instance._value & self.mask) >> self.pos)

    def __set__(self, instance, value):
        # Clear the current value
        instance._value = int(instance._value & ~self.mask)
        # Update with the new value
        instance._value |= int((value << self.pos) & self.mask)


class BasicBitfield(object, metaclass=BitfieldMetaClass):
    _value: int = 0
    # must be overwritten by concrete implementation
    _storage = None

    def set_defaults(self):
        """This function has to be overwritten by concrete implementations to set defaults for the bitfield."""
        raise NotImplementedError

    def __int__(self):
        return self._value

    def __bool__(self):
        return bool(self._value)

    def __init__(self, context=None, arg=0, template=None, set_default=True):
        if set_default:
            self.set_defaults()
        else:
            self._value = 0

    @classmethod
    def from_stream(cls, stream, context=None, arg=0, template=None):
        return cls.from_value(cls._storage.from_stream(stream, context, arg, template))

    @classmethod
    def to_stream(cls, instance, stream, context, arg=0, template=None):
        cls._storage.to_stream(int(instance), stream, context, arg, template)

    @classmethod
    def get_size(cls, instance, context, arg=0, template=None):
        return cls._storage.get_size(instance, context)

    @classmethod
    def from_value(cls, value):
        instance = cls(None, set_default=False)
        instance._value = int(value)
        return instance

    @classmethod
    def from_xml(cls, target, elem, prop, arg=0, template=None):
        return cls.from_value(int(elem.attib[prop], 0))

    @staticmethod
    def to_xml(elem, prop, instance, arg, template, debug):
        elem.attrib[prop] = str(instance._value)

    @staticmethod
    def fmt_member(member, indent=0):
        lines = str(member).split("\n")
        lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
        return "\n".join(lines_new)

    @classmethod
    def validate_instance(cls, instance, context, arg, template):
        cls._storage.validate_instance(int(instance))

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        fields = [(key, getattr(self, key)) for key in self.__members__]
        items = [f"{key} = {str(val)}" for key, val in fields if val is not False]
        info = f"{self.__class__.__name__}: {self._value} {bin(self._value)} {items}"
        # print(info)
        return info

    # rich comparison methods
    def __lt__(self, other):
        return self._value < other

    def __le__(self, other):
        return self._value <= other

    def __eq__(self, other):
        return self._value == other

    def __ne__(self, other):
        return self._value != other

    def __gt__(self, other):
        return self._value > other

    def __ge__(self, other):
        return self._value >= other

    # basic arithmetic functions
    def __add__(self, other):
        return self._value + other

    def __sub__(self, other):
        return self._value - other

    def __mul__(self, other):
        return self._value * other

    def __truediv__(self, other):
        return self._value / other

    def __floordiv__(self, other):
        return self._value // other

    def __mod__(self, other):
        return self._value % other

    def __divmod__(self, other):
        return divmod(self._value, other)

    def __pow__(self, other, modulo=None):
        if modulo is None:
            return pow(self._value, other)
        else:
            return pow(self._value, other, modulo)

    def __lshift__(self, other):
        return self._value << other

    def __rshift__(self, other):
        return self._value >> other

    def __and__(self, other):
        return self._value & other

    def __xor__(self, other):
        return self._value ^ other

    def __or__(self, other):
        return self._value | other

    # reflected basic arithmetic functions
    def __radd__(self, other):
        return other + self._value

    def __rsub__(self, other):
        return other - self._value

    def __rmul__(self, other):
        return other * self._value

    def __rtruediv__(self, other):
        return other / self._value

    def __rfloordiv__(self, other):
        return other // self._value

    def __rmod__(self, other):
        return other % self._value

    def __rdivmod__(self, other):
        return divmod(other, self._value)

    def __rpow__(self, other, modulo=None):
        if modulo is None:
            return pow(other, self._value)
        else:
            return pow(other, self._value, modulo)

    def __rlshift__(self, other):
        return other << self._value

    def __rrshift__(self, other):
        return other >> self._value

    def __rand__(self, other):
        return other & self._value

    def __rxor__(self, other):
        return other ^ self._value

    def __ror__(self, other):
        return other | self._value

    # arithmetic assignments
    def __iadd__(self, other):
        self._value = int(self._value + other)
        return self

    def __isub__(self, other):
        self._value = int(self._value - other)
        return self

    def __imul__(self, other):
        self._value = int(self._value * other)
        return self

    def __itruediv__(self, other):
        self._value = int(self._value / other)
        return self

    def __ifloordiv__(self, other):
        self._value = int(self._value // other)
        return self

    def __imod__(self, other):
        self._value = int(self._value % other)
        return self

    def __ipow__(self, other, modulo=None):
        if modulo is None:
            self._value = int(pow(self._value, other))
        else:
            self._value = int(pow(self._value, other, modulo))
        return self

    def __ilshift__(self, other):
        self._value = int(self._value << other)
        return self

    def __irshift__(self, other):
        self._value = int(self._value >> other)
        return self

    def __iand__(self, other):
        self._value = int(self._value & other)
        return self

    def __ixor__(self, other):
        self._value = int(self._value ^ other)
        return self

    def __ior__(self, other):
        self._value = int(self._value | other)
        return self

    # unary operators
    def __neg__(self):
        return -self._value

    def __pos__(self):
        return +self._value

    def __abs__(self):
        return abs(self._value)

    def __invert__(self):
        return ~self._value

    def __complex__(self):
        return complex(self._value)

    def __float__(self):
        return float(self._value)

    def __index__(self):
        return self.__int__()

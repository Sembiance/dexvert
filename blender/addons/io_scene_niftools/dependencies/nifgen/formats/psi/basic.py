from struct import Struct

import nifgen.formats.base.basic as base_basics
import nifgen.formats.cdf.basic as cdf_basics


class Biguint32(base_basics.class_from_struct(Struct(">I"), lambda value: int(value) % 4294967296)): pass


class Bigushort(base_basics.class_from_struct(Struct(">H"), lambda value: int(value) % 65536)): pass


Ubyte = base_basics.Ubyte
Char = cdf_basics.Char


class LineString:
	"""A variable length string that ends with a newline character (0x0A)."""

	MAX_LEN = base_basics.MAX_LEN

	def __new__(cls, context=None, arg=0, template=None):
		return ''

	@classmethod
	def from_stream(cls, stream, context=None, arg=0, template=None):
		"""The returned string does not include the newline."""
		val = stream.readline(cls.MAX_LEN)
		if val[-1:] != b'\n':
			if len(val) == cls.MAX_LEN:
				raise ValueError('string too long')
			else:
				raise ValueError('Reached end of file before end of {cls.__name__}')
		else:
			val = val[:-1]
		return val.decode(errors="surrogateescape")

	@staticmethod
	def to_stream(instance, stream, context=None, arg=0, template=None):
		stream.write(instance.encode(errors="surrogateescape"))
		stream.write(b'\x0A')

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		return len(instance.encode(errors="surrogateescape")) + 1

	@staticmethod
	def from_value(value, context=None, arg=0, template=None):
		return str(value)

	@staticmethod
	def fmt_member(member, indent=0):
		lines = str(member).split("\n")
		lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
		return "\n".join(lines_new)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert(isinstance(instance, str))
		assert(len(instance.encode(errors="surrogateescape")) <= cls.MAX_LEN)

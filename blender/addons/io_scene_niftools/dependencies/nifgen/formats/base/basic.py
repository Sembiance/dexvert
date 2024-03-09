from ast import literal_eval
import numpy as np
from struct import Struct
from nifgen.array import Array
from nifgen.io import MAX_LEN


def class_from_struct(struct, from_value_func):
	# declare these in the local scope for faster name resolutions
	base_value = from_value_func(0)
	pack = struct.pack
	unpack = struct.unpack
	size = struct.size
	# these functions are used for efficient read/write of arrays
	empty = np.empty
	dtype = np.dtype(struct.format)

	class ConstructedClass:

		np_dtype = dtype

		def __new__(cls, context=None, arg=0, template=None):
			return base_value

		from_value = staticmethod(from_value_func)

		@staticmethod
		def from_stream(stream, context=None, arg=0, template=None):
			return unpack(stream.read(size))[0]

		@staticmethod
		def to_stream(instance, stream, context=None, arg=0, template=None):
			stream.write(pack(instance))

		@staticmethod
		def get_size(instance, context, arg=0, template=None):
			return size

		@staticmethod
		def create_array(shape, default=None, context=None, arg=0, template=None):
			if default:
				return np.full(shape, default, dtype)
			else:
				return np.zeros(shape, dtype)

		@staticmethod
		def read_array(stream, shape, context=None, arg=0, template=None):
			array = empty(shape, dtype)
			stream.readinto(array)
			return array

		@staticmethod
		def write_array(instance, stream):
			# check that it is a numpy array
			if not isinstance(instance, np.ndarray):
				instance = np.array(instance, dtype)
			# cast if wrong incoming dtype
			elif instance.dtype != dtype:
				instance = instance.astype(dtype)
			stream.write(instance.tobytes())

		@staticmethod
		def from_xml(target, elem, prop, arg=0, template=None):
			return literal_eval(elem.attrib[prop])

		@staticmethod
		def _from_xml_array(instance, elem):
			return np.fromstring(elem.text, dtype=dtype, sep=" ")

		@staticmethod
		def to_xml(elem, prop, instance, arg, template, debug):
			elem.attrib[prop] = str(instance)

		@staticmethod
		def _to_xml_array(instance, elem, debug):
			elem.text = " ".join([str(member) for member in instance.flat])

		@staticmethod
		def fmt_member(member, indent=0):
			lines = str(member).split("\n")
			lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
			return "\n".join(lines_new)

		@classmethod
		def validate_instance(cls, instance, context=None, arg=0, template=None):
			assert (instance == cls.from_value(instance))

		@classmethod
		def validate_array(cls, instance, context=None, arg=0, template=None, shape=()):
			assert instance.shape == shape
			assert instance.dtype.char == dtype.char

	return ConstructedClass


Byte = class_from_struct(Struct("<b"), lambda value: (int(value) + 128) % 256 - 128)
Ubyte = class_from_struct(Struct("<B"), lambda value: int(value) % 256)
Uint64 = class_from_struct(Struct("<Q"), lambda value: int(value) % 18446744073709551616)
Uint = class_from_struct(Struct("<I"), lambda value: int(value) % 4294967296)
Ushort = class_from_struct(Struct("<H"), lambda value: int(value) % 65536)
Int = class_from_struct(Struct("<i"), lambda value: (int(value) + 2147483648) % 4294967296 - 2147483648)
Int64 = class_from_struct(Struct("<q"),
						  lambda value: (int(value) + 9223372036854775808) % 18446744073709551616 - 9223372036854775808)
Short = class_from_struct(Struct("<h"), lambda value: (int(value) + 32768) % 65536 - 32768)
Char = Byte
Float = class_from_struct(Struct("<f"), float)
Double = class_from_struct(Struct("<d"), float)
Hfloat = class_from_struct(Struct("<e"), float)


# @staticmethod
def r_zstr(rfunc):
	i = 0
	val = b''
	char = b''
	while char != b'\x00':
		i += 1
		if i > MAX_LEN:
			raise ValueError(f'string too long')
		val += char
		char = rfunc(1)
		if not char:
			raise ValueError('Reached end of file before end of zstring')
	return val.decode(errors="surrogateescape")


# @staticmethod
def w_zstr(wfunc, val):
	wfunc(val.encode(errors="surrogateescape"))
	wfunc(b'\x00')


class ZString:

	def __new__(cls, context=None, arg=0, template=None):
		return ''

	@staticmethod
	def from_stream(stream, context=None, arg=0, template=None):
		return r_zstr(stream.read)

	@staticmethod
	def to_stream(instance, stream, context=None, arg=0, template=None):
		w_zstr(stream.write, instance)

	@staticmethod
	def from_value(value, context=None, arg=0, template=None):
		return str(value)

	@staticmethod
	def from_xml(target, elem, prop, arg=0, template=None):
		return elem[prop]

	@staticmethod
	def to_xml(elem, prop, instance, arg, template, debug):
		elem.attrib[prop] = instance

	@staticmethod
	def fmt_member(member, indent=0):
		lines = str(member).split("\n")
		lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
		return "\n".join(lines_new)

	@classmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		assert (isinstance(instance, str))
		assert (len(instance.encode(errors="surrogateescape")) <= MAX_LEN)

	@staticmethod
	def get_size(instance, context, arg=0, template=None):
		return len(instance.encode(errors="surrogateescape")) + 1


class UNormClass:
	"""Class for floats between 0.0 and 1.0 stored linearly
	This class cannot be used on its own and must be subclassed, with the following class functions/variables defined:
		- storage: the class used for reading/writing
		- from_function: converts the int to the corresponding float
		- to_function: converts the float to the rounded float value
		Both from_function and to_function must work for single values as well as numpy arrays
	Assumptions:
		- storage class has np_type class variable for associated numpy dtype
		- storage class returns np.ndarray for array reading/writing
	"""

	def __new__(cls, context=None, arg=0, template=None):
		return 0.0

	@classmethod
	def from_stream(cls, stream, context, arg, template):
		return cls.from_function(cls.storage.from_stream(stream, context, arg, template))

	@classmethod
	def to_stream(cls, instance, stream, context, arg, template):
		cls.storage.to_stream(int(cls.to_function(instance)), stream, context, arg, template)

	@classmethod
	def get_size(cls, instance, context, arg=0, template=None):
		return cls.storage.get_size(cls.to_function(instance))

	@staticmethod
	def from_value(value):
		# normalized value can range from 0.0 to 1.0
		return min(max(0.0, value), 1.0)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert instance >= 0.0
		assert instance <= 1.0

	@staticmethod
	def fmt_member(member, indent=0):
		lines = str(member).split("\n")
		lines_new = [lines[0], ] + ["\t" * indent + line for line in lines[1:]]
		return "\n".join(lines_new)

	@classmethod
	def create_array(cls, shape, default=None, context=None, arg=0, template=None):
		if default:
			return np.full(shape, default, float)
		else:
			return np.zeros(shape, float)

	@classmethod
	def read_array(cls, stream, shape, context=None, arg=0, template=None):
		return cls.from_function(cls.storage.read_array(stream, shape, context, arg, template).astype(float))

	@classmethod
	def write_array(cls, stream, instance):
		# check that it is a numpy array
		if not isinstance(instance, np.ndarray):
			instance = np.array(instance, float)
		# don't need to cast specifically to float, but do need to convert to byte for writing
		instance = cls.to_function(instance).astype(cls.storage.np_type)
		cls.storage.write_array(stream, instance)


class NormClass(UNormClass):

	@staticmethod
	def from_value(value):
		# signed normalized values can range from -1.0 to 1.0
		return min(max(-1.0, value), 1.0)

	@classmethod
	def validate_instance(cls, instance, context=None, arg=0, template=None):
		assert instance >= -1.0
		assert instance <= 1.0


class Normshort(NormClass):
	storage = Short
	scale = 16383

	@staticmethod
	def from_function(instance):
		return instance / Normshort.scale

	@staticmethod
	def to_function(instance):
		return np.round(instance * Normshort.scale)


class Rangeshort(NormClass):
	storage = Short
	scale = 2048

	@staticmethod
	def from_function(instance):
		return instance / Normshort.scale

	@staticmethod
	def to_function(instance):
		return np.round(instance * Normshort.scale)

import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Vector4(BaseStruct):

	"""
	A 4-dimensional vector.
	"""

	__name__ = 'Vector4'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'x', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'w', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'x', name_type_map['Float'], (0, None), (False, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None)
		yield 'w', name_type_map['Float'], (0, None), (False, None)

	def __init__(self, context=None, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.x = 0
		self.y = 0
		self.z = 0
		self.w = 0

	@classmethod
	def from_value(cls, in_it):
		instance = cls()
		instance.x = in_it[0]
		instance.y = in_it[1]
		instance.z = in_it[2]
		instance.w = in_it[3]
		return instance

	def as_list(self):
		return [self.x, self.y, self.z, self.w]

	def as_tuple(self):
		return (self.x, self.y, self.z, self.w)

	def get_copy(self):
		v = Vector4()
		v.x = self.x
		v.y = self.y
		v.z = self.z
		v.w = self.w
		return v

	def get_vector_3(self):
		v = NifFormat.classes.Vector3()
		v.x = self.x
		v.y = self.y
		v.z = self.z
		return v

	def __str__(self):
		return "[ %6.3f %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z, self.w)

	def __eq__(self, rhs):
		if isinstance(rhs, type(None)):
			return False
		if not isinstance(rhs, Vector4):
			raise TypeError(
				"do not know how to compare Vector4 and %s" % rhs.__class__)
		if abs(self.x - rhs.x) > NifFormat.EPSILON: return False
		if abs(self.y - rhs.y) > NifFormat.EPSILON: return False
		if abs(self.z - rhs.z) > NifFormat.EPSILON: return False
		if abs(self.w - rhs.w) > NifFormat.EPSILON: return False
		return True

	def __ne__(self, rhs):
		return not self.__eq__(rhs)

	@staticmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		name_type_map["Float"].validate_instance(instance.x)
		name_type_map["Float"].validate_instance(instance.y)
		name_type_map["Float"].validate_instance(instance.z)
		name_type_map["Float"].validate_instance(instance.w)


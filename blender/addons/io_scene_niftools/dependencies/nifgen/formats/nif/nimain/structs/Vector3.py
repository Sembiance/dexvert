import math

import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Vector3(BaseStruct):

	"""
	A vector in 3D space (x,y,z).
	"""

	__name__ = 'Vector3'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'x', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'x', name_type_map['Float'], (0, None), (False, None)
		yield 'y', name_type_map['Float'], (0, None), (False, None)
		yield 'z', name_type_map['Float'], (0, None), (False, None)

	def __init__(self, context=None, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.x = 0
		self.y = 0
		self.z = 0

	@classmethod
	def from_value(cls, in_it):
		instance = cls()
		instance.x = in_it[0]
		instance.y = in_it[1]
		instance.z = in_it[2]
		return instance

	def assign(self, vec):
		""" Set this vector to values from another object that supports iteration or x,y,z properties """
		# see if it is an iterable
		try:
			self.x = vec[0]
			self.y = vec[1]
			self.z = vec[2]
		except:
			if hasattr(vec, "x"):
				self.x = vec.x
			if hasattr(vec, "y"):
				self.y = vec.y
			if hasattr(vec, "z"):
				self.z = vec.z
	
	def as_list(self):
		return [self.x, self.y, self.z]

	def as_tuple(self):
		return (self.x, self.y, self.z)

	def norm(self, sqrt=math.sqrt):
		return sqrt(self.x*self.x + self.y*self.y + self.z*self.z)

	def normalize(self, ignore_error=False, sqrt=math.sqrt):
		# inlining norm() to reduce overhead
		try:
			factor = 1.0 / sqrt(self.x*self.x + self.y*self.y + self.z*self.z)
		except ZeroDivisionError:
			if not ignore_error:
				raise
			else:
				return
		# inlining multiplication for speed
		self.x *= factor
		self.y *= factor
		self.z *= factor

	def normalized(self, ignore_error=False):
		vec = self.get_copy()
		vec.normalize(ignore_error=ignore_error)
		return vec

	def get_copy(self):
		v = Vector3()
		v.x = self.x
		v.y = self.y
		v.z = self.z
		return v

	def __str__(self):
		return "[ %6.3f %6.3f %6.3f ]"%(self.x, self.y, self.z)

	def __mul__(self, x):
		if isinstance(x, (float, int)):
			v = Vector3()
			v.x = self.x * x
			v.y = self.y * x
			v.z = self.z * x
			return v
		elif isinstance(x, Vector3):
			return self.x * x.x + self.y * x.y + self.z * x.z
		elif isinstance(x, NifFormat.classes.Matrix33):
			v = Vector3()
			v.x = self.x * x.m_11 + self.y * x.m_21 + self.z * x.m_31
			v.y = self.x * x.m_12 + self.y * x.m_22 + self.z * x.m_32
			v.z = self.x * x.m_13 + self.y * x.m_23 + self.z * x.m_33
			return v
		elif isinstance(x, NifFormat.classes.Matrix44):
			return self * x.get_matrix_33() + x.get_translation()
		else:
			raise TypeError("do not know how to multiply Vector3 with %s"%x.__class__)

	def __rmul__(self, x):
		if isinstance(x, (float, int)):
			v = Vector3()
			v.x = x * self.x
			v.y = x * self.y
			v.z = x * self.z
			return v
		else:
			raise TypeError("do not know how to multiply %s and Vector3"%x.__class__)

	def __div__(self, x):
		if isinstance(x, (float, int)):
			v = Vector3()
			v.x = self.x / x
			v.y = self.y / x
			v.z = self.z / x
			return v
		else:
			raise TypeError("do not know how to divide Vector3 and %s"%x.__class__)

	# py3k
	__truediv__ = __div__

	def __add__(self, x):
		if isinstance(x, (float, int)):
			v = Vector3()
			v.x = self.x + x
			v.y = self.y + x
			v.z = self.z + x
			return v
		elif isinstance(x, Vector3):
			v = Vector3()
			v.x = self.x + x.x
			v.y = self.y + x.y
			v.z = self.z + x.z
			return v
		else:
			raise TypeError("do not know how to add Vector3 and %s"%x.__class__)

	def __radd__(self, x):
		if isinstance(x, (float, int)):
			v = Vector3()
			v.x = x + self.x
			v.y = x + self.y
			v.z = x + self.z
			return v
		else:
			raise TypeError("do not know how to add %s and Vector3"%x.__class__)

	def __sub__(self, x):
		if isinstance(x, (float, int)):
			v = Vector3()
			v.x = self.x - x
			v.y = self.y - x
			v.z = self.z - x
			return v
		elif isinstance(x, Vector3):
			v = Vector3()
			v.x = self.x - x.x
			v.y = self.y - x.y
			v.z = self.z - x.z
			return v
		else:
			raise TypeError("do not know how to substract Vector3 and %s"%x.__class__)

	def __rsub__(self, x):
		if isinstance(x, (float, int)):
			v = Vector3()
			v.x = x - self.x
			v.y = x - self.y
			v.z = x - self.z
			return v
		else:
			raise TypeError("do not know how to substract %s and Vector3"%x.__class__)

	def __neg__(self):
		v = Vector3()
		v.x = -self.x
		v.y = -self.y
		v.z = -self.z
		return v

	# cross product
	def crossproduct(self, x):
		if isinstance(x, Vector3):
			v = Vector3()
			v.x = self.y*x.z - self.z*x.y
			v.y = self.z*x.x - self.x*x.z
			v.z = self.x*x.y - self.y*x.x
			return v
		else:
			raise TypeError("do not know how to calculate crossproduct of Vector3 and %s"%x.__class__)

	def __eq__(self, x):
		if isinstance(x, type(None)):
			return False
		if not isinstance(x, Vector3):
			raise TypeError("do not know how to compare Vector3 and %s" % x.__class__)
		if abs(self.x - x.x) > NifFormat.EPSILON: return False
		if abs(self.y - x.y) > NifFormat.EPSILON: return False
		if abs(self.z - x.z) > NifFormat.EPSILON: return False
		return True

	def __ne__(self, x):
		return not self.__eq__(x)

	@staticmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		name_type_map["Float"].validate_instance(instance.x)
		name_type_map["Float"].validate_instance(instance.y)
		name_type_map["Float"].validate_instance(instance.z)


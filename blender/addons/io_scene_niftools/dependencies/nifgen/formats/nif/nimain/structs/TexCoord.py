import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class TexCoord(BaseStruct):

	"""
	Texture coordinates (u,v). As in OpenGL; image origin is in the lower left corner.
	"""

	__name__ = 'TexCoord'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'u', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'v', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'u', name_type_map['Float'], (0, None), (False, None)
		yield 'v', name_type_map['Float'], (0, None), (False, None)

	def __init__(self, context=None, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u = 0
		self.v = 0

	@classmethod
	def from_value(cls, in_it):
		instance = cls()
		instance.u = in_it[0]
		instance.v = in_it[1]
		return instance

	def as_list(self):
		return [self.u, self.v]

	def normalize(self):
		r = (self.u*self.u + self.v*self.v) ** 0.5
		if r <= NifFormat.EPSILON:
			raise ZeroDivisionError('cannot normalize vector %s'%self)
		self.u /= r
		self.v /= r

	def __str__(self):
		return "[ %6.3f %6.3f ]"%(self.u, self.v)

	def __mul__(self, x):
		if isinstance(x, (float, int)):
			v = TexCoord()
			v.u = self.u * x
			v.v = self.v * x
			return v
		elif isinstance(x, TexCoord):
			return self.u * x.u + self.v * x.v
		else:
			raise TypeError("do not know how to multiply TexCoord with %s"%x.__class__)

	def __rmul__(self, x):
		if isinstance(x, (float, int)):
			v = TexCoord()
			v.u = x * self.u
			v.v = x * self.v
			return v
		else:
			raise TypeError("do not know how to multiply %s and TexCoord"%x.__class__)

	def __add__(self, x):
		if isinstance(x, (float, int)):
			v = TexCoord()
			v.u = self.u + x
			v.v = self.v + x
			return v
		elif isinstance(x, TexCoord):
			v = TexCoord()
			v.u = self.u + x.u
			v.v = self.v + x.v
			return v
		else:
			raise TypeError("do not know how to add TexCoord and %s"%x.__class__)

	def __radd__(self, x):
		if isinstance(x, (float, int)):
			v = TexCoord()
			v.u = x + self.u
			v.v = x + self.v
			return v
		else:
			raise TypeError("do not know how to add %s and TexCoord"%x.__class__)

	def __sub__(self, x):
		if isinstance(x, (float, int)):
			v = TexCoord()
			v.u = self.u - x
			v.v = self.v - x
			return v
		elif isinstance(x, TexCoord):
			v = TexCoord()
			v.u = self.u - x.u
			v.v = self.v - x.v
			return v
		else:
			raise TypeError("do not know how to substract TexCoord and %s"%x.__class__)

	def __rsub__(self, x):
		if isinstance(x, (float, int)):
			v = TexCoord()
			v.u = x - self.u
			v.v = x - self.v
			return v
		else:
			raise TypeError("do not know how to substract %s and TexCoord"%x.__class__)

	def __neg__(self):
		v = TexCoord()
		v.u = -self.u
		v.v = -self.v
		return v

	@staticmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		name_type_map["Float"].validate_instance(instance.u)
		name_type_map["Float"].validate_instance(instance.v)


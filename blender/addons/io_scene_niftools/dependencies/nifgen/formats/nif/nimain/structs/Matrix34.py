import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Matrix34(BaseStruct):

	"""
	A 3x4 transformation matrix.
	"""

	__name__ = 'Matrix34'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'm_11', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'm_21', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_31', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_12', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_22', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'm_32', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_13', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_23', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_33', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'm_14', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_24', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_34', name_type_map['Float'], (0, None), (False, 0.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'm_11', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'm_21', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_31', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_12', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_22', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'm_32', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_13', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_23', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_33', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'm_14', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_24', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_34', name_type_map['Float'], (0, None), (False, 0.0)

	def __init__(self, context=None, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=True)
		self.set_defaults()

	def as_list(self):
		"""Return matrix as 3x3 list."""
		return [
			[self.m_11, self.m_12, self.m_13],
			[self.m_21, self.m_22, self.m_23],
			[self.m_31, self.m_32, self.m_33]
			]

	def as_tuple(self):
		"""Return matrix as 3x3 tuple."""
		return (
			(self.m_11, self.m_12, self.m_13),
			(self.m_21, self.m_22, self.m_23),
			(self.m_31, self.m_32, self.m_33)
			)

	def __str__(self):
		return(
			"[ %6.3f %6.3f %6.3f ]\n"
			"[ %6.3f %6.3f %6.3f ]\n"
			"[ %6.3f %6.3f %6.3f ]\n"
			% (self.m_11, self.m_12, self.m_13,
			   self.m_21, self.m_22, self.m_23,
			   self.m_31, self.m_32, self.m_33))

	def set_identity(self):
		"""Set to identity matrix."""
		self.m_11 = 1.0
		self.m_12 = 0.0
		self.m_13 = 0.0
		self.m_14 = 0.0
		self.m_21 = 0.0
		self.m_22 = 1.0
		self.m_23 = 0.0
		self.m_24 = 0.0
		self.m_31 = 0.0
		self.m_32 = 0.0
		self.m_33 = 1.0
		self.m_34 = 0.0

	def is_identity(self):
		"""Return ``True`` if the matrix is close to identity."""
		if  (abs(self.m_11 - 1.0) > NifFormat.EPSILON
			 or abs(self.m_12) > NifFormat.EPSILON
			 or abs(self.m_13) > NifFormat.EPSILON
			 or abs(self.m_21) > NifFormat.EPSILON
			 or abs(self.m_22 - 1.0) > NifFormat.EPSILON
			 or abs(self.m_23) > NifFormat.EPSILON
			 or abs(self.m_31) > NifFormat.EPSILON
			 or abs(self.m_32) > NifFormat.EPSILON
			 or abs(self.m_33 - 1.0) > NifFormat.EPSILON):
			return False
		else:
			return True

	def get_copy(self):
		"""Return a copy of the matrix."""
		mat = Matrix34()
		mat.m_11 = self.m_11
		mat.m_12 = self.m_12
		mat.m_13 = self.m_13
		mat.m_14 = self.m_14
		mat.m_21 = self.m_21
		mat.m_22 = self.m_22
		mat.m_23 = self.m_23
		mat.m_24 = self.m_24
		mat.m_31 = self.m_31
		mat.m_32 = self.m_32
		mat.m_33 = self.m_33
		mat.m_34 = self.m_34
		return mat

	def __eq__(self, mat):
		if not isinstance(mat, Matrix34):
			raise TypeError(
				"do not know how to compare InertiaMatrix and %s"%mat.__class__)
		if (abs(self.m_11 - mat.m_11) > NifFormat.EPSILON
			or abs(self.m_12 - mat.m_12) > NifFormat.EPSILON
			or abs(self.m_13 - mat.m_13) > NifFormat.EPSILON
			or abs(self.m_21 - mat.m_21) > NifFormat.EPSILON
			or abs(self.m_22 - mat.m_22) > NifFormat.EPSILON
			or abs(self.m_23 - mat.m_23) > NifFormat.EPSILON
			or abs(self.m_31 - mat.m_31) > NifFormat.EPSILON
			or abs(self.m_32 - mat.m_32) > NifFormat.EPSILON
			or abs(self.m_33 - mat.m_33) > NifFormat.EPSILON):
			return False
		return True

	def __ne__(self, mat):
		return not self.__eq__(mat)

	@staticmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		name_type_map["Float"].validate_instance(instance.m_11)
		name_type_map["Float"].validate_instance(instance.m_12)
		name_type_map["Float"].validate_instance(instance.m_13)
		name_type_map["Float"].validate_instance(instance.m_14)
		name_type_map["Float"].validate_instance(instance.m_21)
		name_type_map["Float"].validate_instance(instance.m_22)
		name_type_map["Float"].validate_instance(instance.m_23)
		name_type_map["Float"].validate_instance(instance.m_24)
		name_type_map["Float"].validate_instance(instance.m_31)
		name_type_map["Float"].validate_instance(instance.m_32)
		name_type_map["Float"].validate_instance(instance.m_33)
		name_type_map["Float"].validate_instance(instance.m_34)


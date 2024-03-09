import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Matrix33(BaseStruct):

	"""
	A 3x3 rotation matrix; M^T M=identity, det(M)=1.    Stored in OpenGL column-major format.
	"""

	__name__ = 'Matrix33'


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
		return (
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
		self.m_21 = 0.0
		self.m_22 = 1.0
		self.m_23 = 0.0
		self.m_31 = 0.0
		self.m_32 = 0.0
		self.m_33 = 1.0

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
		mat = Matrix33()
		mat.m_11 = self.m_11
		mat.m_12 = self.m_12
		mat.m_13 = self.m_13
		mat.m_21 = self.m_21
		mat.m_22 = self.m_22
		mat.m_23 = self.m_23
		mat.m_31 = self.m_31
		mat.m_32 = self.m_32
		mat.m_33 = self.m_33
		return mat

	def get_transpose(self):
		"""Get transposed of the matrix."""
		mat = Matrix33()
		mat.m_11 = self.m_11
		mat.m_12 = self.m_21
		mat.m_13 = self.m_31
		mat.m_21 = self.m_12
		mat.m_22 = self.m_22
		mat.m_23 = self.m_32
		mat.m_31 = self.m_13
		mat.m_32 = self.m_23
		mat.m_33 = self.m_33
		return mat

	def is_scale_rotation(self):
		"""Returns true if the matrix decomposes nicely into scale * rotation."""
		# NOTE: 0.01 instead of EPSILON to work around bad NIF files

		# calculate self * self^T
		# this should correspond to
		# (scale * rotation) * (scale * rotation)^T
		# = scale^2 * rotation * rotation^T
		# = scale^2 * 3x3 identity matrix
		self_transpose = self.get_transpose()
		mat = self * self_transpose

		# off diagonal elements should be zero
		if (abs(mat.m_12) + abs(mat.m_13)
			+ abs(mat.m_21) + abs(mat.m_23)
			+ abs(mat.m_31) + abs(mat.m_32)) > 0.01:
			return False

		# diagonal elements should be equal (to scale^2)
		if abs(mat.m_11 - mat.m_22) + abs(mat.m_22 - mat.m_33) > 0.01:
			return False

		return True

	def is_rotation(self):
		"""Returns ``True`` if the matrix is a rotation matrix
		(a member of SO(3))."""
		# NOTE: 0.01 instead of NifFormat.EPSILON to work around bad NIF files

		if not self.is_scale_rotation():
			return False
		if abs(self.get_determinant() - 1.0) > 0.01:
			return False
		return True

	def get_determinant(self):
		"""Return determinant."""
		return (self.m_11*self.m_22*self.m_33
				+self.m_12*self.m_23*self.m_31
				+self.m_13*self.m_21*self.m_32
				-self.m_31*self.m_22*self.m_13
				-self.m_21*self.m_12*self.m_33
				-self.m_11*self.m_32*self.m_23)

	def get_scale(self):
		"""Gets the scale (assuming is_scale_rotation is true!)."""
		scale = self.get_determinant()
		if scale < 0:
			return -((-scale)**(1.0/3.0))
		else:
			return scale**(1.0/3.0)

	def get_scale_rotation(self):
		"""Decompose the matrix into scale and rotation, where scale is a float
		and rotation is a C{Matrix33}. Returns a pair (scale, rotation)."""
		rot = self.get_copy()
		scale = self.get_scale()
		if abs(scale) <= NifFormat.EPSILON:
			raise ZeroDivisionError('scale is zero, unable to obtain rotation')
		rot /= scale
		return (scale, rot)

	def set_scale_rotation(self, scale, rotation):
		"""Compose the matrix as the product of scale * rotation."""
		if not isinstance(scale, (float, int)):
			raise TypeError('scale must be float')
		if not isinstance(rotation, Matrix33):
			raise TypeError('rotation must be Matrix33')

		if not rotation.is_rotation():
			raise ValueError('rotation must be rotation matrix')

		self.m_11 = rotation.m_11 * scale
		self.m_12 = rotation.m_12 * scale
		self.m_13 = rotation.m_13 * scale
		self.m_21 = rotation.m_21 * scale
		self.m_22 = rotation.m_22 * scale
		self.m_23 = rotation.m_23 * scale
		self.m_31 = rotation.m_31 * scale
		self.m_32 = rotation.m_32 * scale
		self.m_33 = rotation.m_33 * scale

	def get_scale_quat(self):
		"""Decompose matrix into scale and quaternion."""
		scale, rot = self.get_scale_rotation()
		quat = NifFormat.classes.Quaternion(self.context)
		trace = 1.0 + rot.m_11 + rot.m_22 + rot.m_33

		if trace > NifFormat.EPSILON:
			s = (trace ** 0.5) * 2
			quat.x = -( rot.m_32 - rot.m_23 ) / s
			quat.y = -( rot.m_13 - rot.m_31 ) / s
			quat.z = -( rot.m_21 - rot.m_12 ) / s
			quat.w = 0.25 * s
		elif rot.m_11 > max((rot.m_22, rot.m_33)):
			s  = (( 1.0 + rot.m_11 - rot.m_22 - rot.m_33 ) ** 0.5) * 2
			quat.x = 0.25 * s
			quat.y = (rot.m_21 + rot.m_12 ) / s
			quat.z = (rot.m_13 + rot.m_31 ) / s
			quat.w = -(rot.m_32 - rot.m_23 ) / s
		elif rot.m_22 > rot.m_33:
			s  = (( 1.0 + rot.m_22 - rot.m_11 - rot.m_33 ) ** 0.5) * 2
			quat.x = (rot.m_21 + rot.m_12 ) / s
			quat.y = 0.25 * s
			quat.z = (rot.m_32 + rot.m_23 ) / s
			quat.w = -(rot.m_13 - rot.m_31 ) / s
		else:
			s  = (( 1.0 + rot.m_33 - rot.m_11 - rot.m_22 ) ** 0.5) * 2
			quat.x = (rot.m_13 + rot.m_31 ) / s
			quat.y = (rot.m_32 + rot.m_23 ) / s
			quat.z = 0.25 * s
			quat.w = -(rot.m_21 - rot.m_12 ) / s

		return scale, quat


	def get_inverse(self):
		"""Get inverse (assuming is_scale_rotation is true!)."""
		# transpose inverts rotation but keeps the scale
		# dividing by scale^2 inverts the scale as well
		return self.get_transpose() / (self.m_11**2 + self.m_12**2 + self.m_13**2)

	def __mul__(self, rhs):
		if isinstance(rhs, (float, int)):
			mat = Matrix33()
			mat.m_11 = self.m_11 * rhs
			mat.m_12 = self.m_12 * rhs
			mat.m_13 = self.m_13 * rhs
			mat.m_21 = self.m_21 * rhs
			mat.m_22 = self.m_22 * rhs
			mat.m_23 = self.m_23 * rhs
			mat.m_31 = self.m_31 * rhs
			mat.m_32 = self.m_32 * rhs
			mat.m_33 = self.m_33 * rhs
			return mat
		elif isinstance(rhs, NifFormat.classes.Vector3):
			raise TypeError(
				"matrix*vector not supported; "
				"please use left multiplication (vector*matrix)")
		elif isinstance(rhs, Matrix33):
			mat = Matrix33()
			mat.m_11 = self.m_11 * rhs.m_11 + self.m_12 * rhs.m_21 + self.m_13 * rhs.m_31
			mat.m_12 = self.m_11 * rhs.m_12 + self.m_12 * rhs.m_22 + self.m_13 * rhs.m_32
			mat.m_13 = self.m_11 * rhs.m_13 + self.m_12 * rhs.m_23 + self.m_13 * rhs.m_33
			mat.m_21 = self.m_21 * rhs.m_11 + self.m_22 * rhs.m_21 + self.m_23 * rhs.m_31
			mat.m_22 = self.m_21 * rhs.m_12 + self.m_22 * rhs.m_22 + self.m_23 * rhs.m_32
			mat.m_23 = self.m_21 * rhs.m_13 + self.m_22 * rhs.m_23 + self.m_23 * rhs.m_33
			mat.m_31 = self.m_31 * rhs.m_11 + self.m_32 * rhs.m_21 + self.m_33 * rhs.m_31
			mat.m_32 = self.m_31 * rhs.m_12 + self.m_32 * rhs.m_22 + self.m_33 * rhs.m_32
			mat.m_33 = self.m_31 * rhs.m_13 + self.m_32 * rhs.m_23 + self.m_33 * rhs.m_33
			return mat
		else:
			raise TypeError(
				"do not know how to multiply Matrix33 with %s"%rhs.__class__)

	def __div__(self, rhs):
		if isinstance(rhs, (float, int)):
			mat = Matrix33()
			mat.m_11 = self.m_11 / rhs
			mat.m_12 = self.m_12 / rhs
			mat.m_13 = self.m_13 / rhs
			mat.m_21 = self.m_21 / rhs
			mat.m_22 = self.m_22 / rhs
			mat.m_23 = self.m_23 / rhs
			mat.m_31 = self.m_31 / rhs
			mat.m_32 = self.m_32 / rhs
			mat.m_33 = self.m_33 / rhs
			return mat
		else:
			raise TypeError(
				"do not know how to divide Matrix33 by %s"%rhs.__class__)

	# py3k
	__truediv__ = __div__

	def __rmul__(self, lhs):
		if isinstance(lhs, (float, int)):
			return self * lhs # commutes
		else:
			raise TypeError(
				"do not know how to multiply %s with Matrix33"%lhs.__class__)

	def __eq__(self, mat):
		if not isinstance(mat, Matrix33):
			raise TypeError(
				"do not know how to compare Matrix33 and %s"%mat.__class__)
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

	def __sub__(self, x):
		if isinstance(x, (Matrix33)):
			m = Matrix33()
			m.m_11 = self.m_11 - x.m_11
			m.m_12 = self.m_12 - x.m_12
			m.m_13 = self.m_13 - x.m_13
			m.m_21 = self.m_21 - x.m_21
			m.m_22 = self.m_22 - x.m_22
			m.m_23 = self.m_23 - x.m_23
			m.m_31 = self.m_31 - x.m_31
			m.m_32 = self.m_32 - x.m_32
			m.m_33 = self.m_33 - x.m_33
			return m
		elif isinstance(x, (int, float)):
			m = Matrix33()
			m.m_11 = self.m_11 - x
			m.m_12 = self.m_12 - x
			m.m_13 = self.m_13 - x
			m.m_21 = self.m_21 - x
			m.m_22 = self.m_22 - x
			m.m_23 = self.m_23 - x
			m.m_31 = self.m_31 - x
			m.m_32 = self.m_32 - x
			m.m_33 = self.m_33 - x
			return m
		else:
			raise TypeError("do not know how to substract Matrix33 and %s"
							% x.__class__)

	def sup_norm(self):
		"""Calculate supremum norm of matrix (maximum absolute value of all
		entries)."""
		return max(max(abs(elem) for elem in row)
				   for row in self.as_list())

	@staticmethod
	def validate_instance(instance, context=None, arg=0, template=None):
		name_type_map["Float"].validate_instance(instance.m_11)
		name_type_map["Float"].validate_instance(instance.m_12)
		name_type_map["Float"].validate_instance(instance.m_13)
		name_type_map["Float"].validate_instance(instance.m_21)
		name_type_map["Float"].validate_instance(instance.m_22)
		name_type_map["Float"].validate_instance(instance.m_23)
		name_type_map["Float"].validate_instance(instance.m_31)
		name_type_map["Float"].validate_instance(instance.m_32)
		name_type_map["Float"].validate_instance(instance.m_33)


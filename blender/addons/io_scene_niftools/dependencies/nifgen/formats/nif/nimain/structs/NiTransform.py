import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiTransform(BaseStruct):

	__name__ = 'NiTransform'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The rotation part of the transformation matrix.
		self.rotation = name_type_map['Matrix33'](self.context, 0, None)

		# The translation vector.
		self.translation = name_type_map['Vector3'](self.context, 0, None)

		# Scaling part (only uniform scaling is supported).
		self.scale = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0)
	def get_transform(self):
		"""Return scale, rotation, and translation into a single 4x4 matrix."""
		mat = NifFormat.classes.Matrix44()
		mat.set_scale_rotation_translation(
			self.scale,
			self.rotation,
			self.translation)
		return mat

	def set_transform(self, mat):
		"""Set rotation, transform, and velocity."""
		scale, rotation, translation = mat.get_scale_rotation_translation()

		self.scale = scale

		self.rotation.m_11 = rotation.m_11
		self.rotation.m_12 = rotation.m_12
		self.rotation.m_13 = rotation.m_13
		self.rotation.m_21 = rotation.m_21
		self.rotation.m_22 = rotation.m_22
		self.rotation.m_23 = rotation.m_23
		self.rotation.m_31 = rotation.m_31
		self.rotation.m_32 = rotation.m_32
		self.rotation.m_33 = rotation.m_33

		self.translation.x = translation.x
		self.translation.y = translation.y
		self.translation.z = translation.z


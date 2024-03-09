import nifgen.formats.nif as NifFormat
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BSSkinBoneTrans(BaseStruct):

	"""
	Fallout 4 Bone Transform
	"""

	__name__ = 'BSSkinBoneTrans'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.bounding_sphere = name_type_map['NiBound'](self.context, 0, None)
		self.rotation = name_type_map['Matrix33'](self.context, 0, None)
		self.translation = name_type_map['Vector3'](self.context, 0, None)
		self.scale = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'bounding_sphere', name_type_map['NiBound'], (0, None), (False, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, None)
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


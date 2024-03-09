from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BhkQsTransform(BaseStruct):

	"""
	Bethesda extension of hkQsTransform. The scale vector is not serialized.
	"""

	__name__ = 'bhkQsTransform'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# A vector that moves the chunk by the specified amount. W is not used.
		self.translation = name_type_map['Vector4'](self.context, 0, None)

		# Rotation. Reference point for rotation is bhkRigidBody translation.
		self.rotation = name_type_map['HkQuaternion'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'translation', name_type_map['Vector4'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['HkQuaternion'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'translation', name_type_map['Vector4'], (0, None), (False, None)
		yield 'rotation', name_type_map['HkQuaternion'], (0, None), (False, None)

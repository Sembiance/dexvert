from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class JointTransform(BaseStruct):

	"""
	Describes a joint in armature space.
	"""

	__name__ = 'JointTransform'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# the rotation of the joint, inverted
		self.rot = name_type_map['Matrix33'](self.context, 0, None)

		# the location of the joint
		self.loc = name_type_map['Vector3'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'rot', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'rot', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'loc', name_type_map['Vector3'], (0, None), (False, None)

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiQuatTransform(BaseStruct):

	__name__ = 'NiQuatTransform'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.translation = name_type_map['Vector3'](self.context, 0, None)
		self.rotation = name_type_map['Quaternion'](self.context, 0, None)
		self.scale = name_type_map['Float'].from_value(1.0)

		# Whether each transform component is valid.
		self.trs_valid = Array(self.context, 0, None, (0,), name_type_map['Bool'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['Quaternion'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'trs_valid', Array, (0, None, (3,), name_type_map['Bool']), (False, None), (lambda context: context.version <= 167837805, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None)
		yield 'rotation', name_type_map['Quaternion'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.version <= 167837805:
			yield 'trs_valid', Array, (0, None, (3,), name_type_map['Bool']), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor <scale> on data."""
		self.translation.x *= scale
		self.translation.y *= scale
		self.translation.z *= scale

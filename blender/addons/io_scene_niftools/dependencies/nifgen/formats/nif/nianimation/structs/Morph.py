from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Morph(BaseStruct):

	"""
	Geometry morphing data component.
	"""

	__name__ = 'Morph'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Name of the frame.
		self.frame_name = name_type_map['String'](self.context, 0, None)

		# The number of morph keys that follow.
		self.num_keys = name_type_map['Uint'](self.context, 0, None)

		# Unlike most objects, the presense of this value is not conditional on there being keys.
		self.interpolation = name_type_map['KeyType'](self.context, 0, None)

		# The morph key frames.
		self.keys = Array(self.context, self.interpolation, name_type_map['Float'], (0,), name_type_map['Key'])
		self.legacy_weight = name_type_map['Float'](self.context, 0, None)

		# Morph vectors.
		self.vectors = Array(self.context, 0, None, (0,), name_type_map['Vector3'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'frame_name', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 167837802, None)
		yield 'num_keys', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 167837696, None)
		yield 'interpolation', name_type_map['KeyType'], (0, None), (False, None), (lambda context: context.version <= 167837696, None)
		yield 'keys', Array, (None, name_type_map['Float'], (None,), name_type_map['Key']), (False, None), (lambda context: context.version <= 167837696, None)
		yield 'legacy_weight', name_type_map['Float'], (0, None), (False, None), (lambda context: 167837800 <= context.version <= 335609858 and context.bs_header.bs_version < 10, None)
		yield 'vectors', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837802:
			yield 'frame_name', name_type_map['String'], (0, None), (False, None)
		if instance.context.version <= 167837696:
			yield 'num_keys', name_type_map['Uint'], (0, None), (False, None)
			yield 'interpolation', name_type_map['KeyType'], (0, None), (False, None)
			yield 'keys', Array, (instance.interpolation, name_type_map['Float'], (instance.num_keys,), name_type_map['Key']), (False, None)
		if 167837800 <= instance.context.version <= 335609858 and instance.context.bs_header.bs_version < 10:
			yield 'legacy_weight', name_type_map['Float'], (0, None), (False, None)
		yield 'vectors', Array, (0, None, (instance.arg,), name_type_map['Vector3']), (False, None)

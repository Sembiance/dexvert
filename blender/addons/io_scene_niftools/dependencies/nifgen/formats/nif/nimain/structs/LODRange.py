from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class LODRange(BaseStruct):

	"""
	The distance range where a specific level of detail applies.
	"""

	__name__ = 'LODRange'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Beginning of range.
		self.near_extent = name_type_map['Float'](self.context, 0, None)

		# End of Range.
		self.far_extent = name_type_map['Float'](self.context, 0, None)
		self.unknown_ints = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'near_extent', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'far_extent', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unknown_ints', Array, (0, None, (3,), name_type_map['Uint']), (False, None), (lambda context: context.version <= 50397184, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'near_extent', name_type_map['Float'], (0, None), (False, None)
		yield 'far_extent', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version <= 50397184:
			yield 'unknown_ints', Array, (0, None, (3,), name_type_map['Uint']), (False, None)

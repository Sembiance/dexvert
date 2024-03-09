from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class NiSortAdjustNode(NiNode):

	"""
	Used to turn sorting off for individual subtrees in a scene. Useful if objects must be drawn in a fixed order.
	"""

	__name__ = 'NiSortAdjustNode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Sorting
		self.sorting_mode = name_type_map['SortingMode'].SORTING_INHERIT
		self.accumulator = name_type_map['Ref'](self.context, 0, name_type_map['NiAccumulator'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'sorting_mode', name_type_map['SortingMode'], (0, None), (False, name_type_map['SortingMode'].SORTING_INHERIT), (None, None)
		yield 'accumulator', name_type_map['Ref'], (0, name_type_map['NiAccumulator']), (False, None), (lambda context: context.version <= 335544323, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'sorting_mode', name_type_map['SortingMode'], (0, None), (False, name_type_map['SortingMode'].SORTING_INHERIT)
		if instance.context.version <= 335544323:
			yield 'accumulator', name_type_map['Ref'], (0, name_type_map['NiAccumulator']), (False, None)

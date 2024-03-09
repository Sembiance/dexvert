from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.trackstation.imports import name_type_map


class FirstPointersb(MemStruct):

	"""
	PZ and PC: 112 bytes
	"""

	__name__ = 'FirstPointersb'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.pointer_stuff = name_type_map['CommonChunk'](self.context, 0, None)
		self.zero = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pointer_stuff', name_type_map['CommonChunk'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pointer_stuff', name_type_map['CommonChunk'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None)

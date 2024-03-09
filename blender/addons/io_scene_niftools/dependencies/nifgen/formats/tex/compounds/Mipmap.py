from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.tex.imports import name_type_map


class Mipmap(MemStruct):

	"""
	Describes one tex mipmap
	"""

	__name__ = 'Mipmap'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# starting offset into the texture buffer for this mip level
		self.offset = name_type_map['Uint'](self.context, 0, None)

		# bytes for one array tile, including padding
		self.size = name_type_map['Uint'](self.context, 0, None)

		# bytes for all array tile, including padding
		self.size_array = name_type_map['Uint'](self.context, 0, None)

		# size of a scan line of blocks, including padding that is added to the end of the line
		self.size_scan = name_type_map['Uint'](self.context, 0, None)

		# size of all non-empty scanline blocks (including padding), ie. the last mips add an empty scanline which does not count
		self.size_data = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'size_array', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'size_scan', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'size_data', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'size', name_type_map['Uint'], (0, None), (False, None)
		yield 'size_array', name_type_map['Uint'], (0, None), (False, None)
		yield 'size_scan', name_type_map['Uint'], (0, None), (False, None)
		yield 'size_data', name_type_map['Uint'], (0, None), (False, None)

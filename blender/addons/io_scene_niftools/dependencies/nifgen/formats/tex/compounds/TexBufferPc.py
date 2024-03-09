from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.tex.imports import name_type_map


class TexBufferPc(MemStruct):

	"""
	The different tex buffers contain the smallest mip
	"""

	__name__ = 'TexBufferPc'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.width = name_type_map['Ushort'](self.context, 0, None)
		self.height = name_type_map['Ushort'](self.context, 0, None)

		# may be depth
		self.num_tiles = name_type_map['Ushort'](self.context, 0, None)

		# the first ie. biggest levels are clipped off
		self.num_mips = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'width', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'height', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_tiles', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 18, None)
		yield 'num_mips', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'width', name_type_map['Ushort'], (0, None), (False, None)
		yield 'height', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version >= 18:
			yield 'num_tiles', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_mips', name_type_map['Ushort'], (0, None), (False, None)

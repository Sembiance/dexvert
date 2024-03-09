from nifgen.formats.matcol.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class MatcolRoot(MemStruct):

	"""
	root_entry data
	"""

	__name__ = 'MatcolRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# always 1
		self.one = name_type_map['Uint64'](self.context, 0, None)
		self.main = name_type_map['Pointer'](self.context, 0, name_type_map['RootFrag'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'main', name_type_map['Pointer'], (0, name_type_map['RootFrag']), (False, None), (None, None)
		yield 'one', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'main', name_type_map['Pointer'], (0, name_type_map['RootFrag']), (False, None)
		yield 'one', name_type_map['Uint64'], (0, None), (False, None)

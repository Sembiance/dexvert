from nifgen.formats.fgm.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class GenericInfo(MemStruct):

	__name__ = 'GenericInfo'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# byte offset to name in fgm buffer
		self._name_offset = name_type_map['Uint'](self.context, 0, None)
		self.dtype = name_type_map['FgmDtype'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield '_name_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'dtype', name_type_map['FgmDtype'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield '_name_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'dtype', name_type_map['FgmDtype'], (0, None), (False, None)

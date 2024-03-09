from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niobjects.MdlManCDataEntry import MdlManCDataEntry


class MdlManCModelTemplateDataEntry(MdlManCDataEntry):

	__name__ = 'MdlMan::CModelTemplateDataEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.max_bound_extra_data = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatsExtraData'])
		self.num_sub_entry_list = name_type_map['Uint'](self.context, 0, None)
		self.sub_entry_list = Array(self.context, 0, name_type_map['MdlManCDataEntry'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'max_bound_extra_data', name_type_map['Ref'], (0, name_type_map['NiFloatsExtraData']), (False, None), (None, None)
		yield 'num_sub_entry_list', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'sub_entry_list', Array, (0, name_type_map['MdlManCDataEntry'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'max_bound_extra_data', name_type_map['Ref'], (0, name_type_map['NiFloatsExtraData']), (False, None)
		yield 'num_sub_entry_list', name_type_map['Uint'], (0, None), (False, None)
		yield 'sub_entry_list', Array, (0, name_type_map['MdlManCDataEntry'], (instance.num_sub_entry_list,), name_type_map['Ref']), (False, None)

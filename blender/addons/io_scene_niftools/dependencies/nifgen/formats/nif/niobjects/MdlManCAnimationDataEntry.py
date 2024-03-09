from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niobjects.MdlManCDataEntry import MdlManCDataEntry


class MdlManCAnimationDataEntry(MdlManCDataEntry):

	__name__ = 'MdlMan::CAnimationDataEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_controller_seq_list = name_type_map['Uint'](self.context, 0, None)
		self.controller_seq_list = Array(self.context, 0, name_type_map['NiControllerSequence'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_controller_seq_list', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'controller_seq_list', Array, (0, name_type_map['NiControllerSequence'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_controller_seq_list', name_type_map['Uint'], (0, None), (False, None)
		yield 'controller_seq_list', Array, (0, name_type_map['NiControllerSequence'], (instance.num_controller_seq_list,), name_type_map['Ref']), (False, None)

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niobjects.MdlManCDataEntry import MdlManCDataEntry


class MdlManCSkeletonDataEntry(MdlManCDataEntry):

	__name__ = 'MdlMan::CSkeletonDataEntry'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.skeleton_data_reference = name_type_map['Ref'](self.context, 0, name_type_map['NiAVObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'skeleton_data_reference', name_type_map['Ref'], (0, name_type_map['NiAVObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'skeleton_data_reference', name_type_map['Ref'], (0, name_type_map['NiAVObject']), (False, None)

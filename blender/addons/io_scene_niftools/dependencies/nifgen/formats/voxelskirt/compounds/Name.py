from nifgen.base_struct import BaseStruct
from nifgen.formats.voxelskirt.imports import name_type_map


class Name(BaseStruct):

	__name__ = 'Name'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# address of ZString
		self._offset = name_type_map['Uint64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield '_offset', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield '_offset', name_type_map['Uint64'], (0, None), (False, None)

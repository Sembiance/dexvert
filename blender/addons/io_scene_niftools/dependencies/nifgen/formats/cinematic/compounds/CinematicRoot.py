from nifgen.formats.cinematic.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class CinematicRoot(MemStruct):

	__name__ = 'CinematicRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.u_0 = name_type_map['Uint64'](self.context, 0, None)
		self.u_1 = name_type_map['Uint64'](self.context, 0, None)
		self.data = name_type_map['Pointer'](self.context, 0, name_type_map['CinematicData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'u_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['Pointer'], (0, name_type_map['CinematicData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'u_0', name_type_map['Uint64'], (0, None), (False, None)
		yield 'u_1', name_type_map['Uint64'], (0, None), (False, None)
		yield 'data', name_type_map['Pointer'], (0, name_type_map['CinematicData']), (False, None)

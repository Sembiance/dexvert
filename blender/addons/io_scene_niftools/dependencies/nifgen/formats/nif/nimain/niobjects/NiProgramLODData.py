from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiLODData import NiLODData


class NiProgramLODData(NiLODData):

	__name__ = 'NiProgramLODData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unknown_uint = name_type_map['Uint'](self.context, 0, None)

		# Guess is that this is the number of LOD entries, but unsure given that there was only one example.
		self.num_lod_entries = name_type_map['Uint'](self.context, 0, None)
		self.lod_entries = Array(self.context, 0, None, (0,), name_type_map['QQSpeedLODEntry'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_uint', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'num_lod_entries', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'lod_entries', Array, (0, None, (None,), name_type_map['QQSpeedLODEntry']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unknown_uint', name_type_map['Uint'], (0, None), (False, None)
		yield 'num_lod_entries', name_type_map['Uint'], (0, None), (False, None)
		yield 'lod_entries', Array, (0, None, (instance.num_lod_entries,), name_type_map['QQSpeedLODEntry']), (False, None)

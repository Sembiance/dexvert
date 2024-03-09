from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.bnk.imports import name_type_map


class HIRCSection(BaseStruct):

	"""
	The HIRC section contains all the Wwise objects, including the events, the containers to group sounds, and the references to the sound files.
	"""

	__name__ = 'HIRCSection'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# length of following data
		self.length = name_type_map['Uint'](self.context, 0, None)
		self.count = name_type_map['Uint'](self.context, 0, None)
		self.hirc_pointers = Array(self.context, 0, None, (0,), name_type_map['HircPointer'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'length', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'count', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'hirc_pointers', Array, (0, None, (None,), name_type_map['HircPointer']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'length', name_type_map['Uint'], (0, None), (False, None)
		yield 'count', name_type_map['Uint'], (0, None), (False, None)
		yield 'hirc_pointers', Array, (0, None, (instance.count,), name_type_map['HircPointer']), (False, None)

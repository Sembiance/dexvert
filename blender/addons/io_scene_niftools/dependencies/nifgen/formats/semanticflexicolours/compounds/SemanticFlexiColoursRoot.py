from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.semanticflexicolours.imports import name_type_map


class SemanticFlexiColoursRoot(MemStruct):

	__name__ = 'SemanticFlexiColoursRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name_count = name_type_map['Uint64'](self.context, 0, None)
		self.name_list = name_type_map['ArrayPointer'](self.context, self.name_count, name_type_map['Colourname'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name_list', name_type_map['ArrayPointer'], (None, name_type_map['Colourname']), (False, None), (None, None)
		yield 'name_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name_list', name_type_map['ArrayPointer'], (instance.name_count, name_type_map['Colourname']), (False, None)
		yield 'name_count', name_type_map['Uint64'], (0, None), (False, None)

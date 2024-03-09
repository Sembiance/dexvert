from nifgen.formats.dinosaurmaterialvariants.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class DinoVariantsHeader(MemStruct):

	"""
	# set_count - seen either 0 or 1, could possibly be more, would need refactor in that case
	# no set_count for rex 93 - has no materialpatterns, so that's probably why it's different
	"""

	__name__ = 'DinoVariantsHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.has_sets = name_type_map['Uint64'](self.context, 0, None)
		self.variant_count = name_type_map['Uint64'](self.context, 0, None)
		self.zero = name_type_map['Uint64'](self.context, 0, None)
		self.fgm_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZStringObfuscated'])
		self.set_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.variants = name_type_map['Pointer'](self.context, self.variant_count, name_type_map['VariantArray'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'fgm_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None), (None, None)
		yield 'has_sets', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'set_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'variants', name_type_map['Pointer'], (None, name_type_map['VariantArray']), (False, None), (None, None)
		yield 'variant_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'fgm_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None)
		yield 'has_sets', name_type_map['Uint64'], (0, None), (False, None)
		yield 'set_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'variants', name_type_map['Pointer'], (instance.variant_count, name_type_map['VariantArray']), (False, None)
		yield 'variant_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint64'], (0, None), (False, None)

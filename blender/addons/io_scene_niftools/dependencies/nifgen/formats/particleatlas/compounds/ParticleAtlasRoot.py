from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.particleatlas.imports import name_type_map


class ParticleAtlasRoot(MemStruct):

	__name__ = 'ParticleAtlasRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# matches number in tex file name
		self.id = name_type_map['Uint'](self.context, 0, None)
		self.zero = name_type_map['Uint'](self.context, 0, None)
		self.tex_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])
		self.gfr_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZString'])

		# tex file used by atlas
		self.dependency_name = name_type_map['Pointer'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'tex_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'gfr_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None), (None, None)
		yield 'id', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'dependency_name', name_type_map['Pointer'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'tex_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'gfr_name', name_type_map['Pointer'], (0, name_type_map['ZString']), (False, None)
		yield 'id', name_type_map['Uint'], (0, None), (False, None)
		yield 'zero', name_type_map['Uint'], (0, None), (False, None)
		yield 'dependency_name', name_type_map['Pointer'], (0, None), (False, None)

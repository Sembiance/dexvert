from nifgen.formats.matcol.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class RootFrag(MemStruct):

	"""
	first frag data
	(3=variant, 2=layered)
	"""

	__name__ = 'RootFrag'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.mat_type = name_type_map['Uint64'](self.context, 0, None)
		self.tex_count = name_type_map['Uint64'](self.context, 0, None)
		self.mat_count = name_type_map['Uint64'](self.context, 0, None)
		self.unk = name_type_map['Uint64'](self.context, 0, None)
		self.textures = name_type_map['ArrayPointer'](self.context, self.tex_count, name_type_map['Texture'])
		self.materials = name_type_map['ArrayPointer'](self.context, self.mat_count, name_type_map['LayerFrag'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'mat_type', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'textures', name_type_map['ArrayPointer'], (None, name_type_map['Texture']), (False, None), (None, None)
		yield 'tex_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'materials', name_type_map['ArrayPointer'], (None, name_type_map['LayerFrag']), (False, None), (None, None)
		yield 'mat_count', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'mat_type', name_type_map['Uint64'], (0, None), (False, None)
		yield 'textures', name_type_map['ArrayPointer'], (instance.tex_count, name_type_map['Texture']), (False, None)
		yield 'tex_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'materials', name_type_map['ArrayPointer'], (instance.mat_count, name_type_map['LayerFrag']), (False, None)
		yield 'mat_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'unk', name_type_map['Uint64'], (0, None), (False, None)

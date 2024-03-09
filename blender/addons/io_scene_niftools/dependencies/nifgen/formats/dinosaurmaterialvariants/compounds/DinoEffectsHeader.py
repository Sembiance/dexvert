from nifgen.array import Array
from nifgen.formats.dinosaurmaterialvariants.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class DinoEffectsHeader(MemStruct):

	__name__ = 'DinoEffectsHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.vec_0 = name_type_map['Vector3F'](self.context, 0, None)
		self.vec_1 = name_type_map['Vector3F'](self.context, 0, None)
		self.a = name_type_map['Uint'](self.context, 0, None)
		self.b = name_type_map['Uint'](self.context, 0, None)
		self.vec_2 = name_type_map['Vector3F'](self.context, 0, None)
		self.vec_3 = name_type_map['Vector3F'](self.context, 0, None)
		self.vec_4 = name_type_map['Vector3F'](self.context, 0, None)
		self.vec_5 = name_type_map['Vector3F'](self.context, 0, None)
		self.c = name_type_map['Uint'](self.context, 0, None)
		self.d = name_type_map['Uint'](self.context, 0, None)
		self.floats_1 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.e = name_type_map['Uint'](self.context, 0, None)
		self.floats_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.f = name_type_map['Uint'](self.context, 0, None)
		self.floats_3 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.g = name_type_map['Uint'](self.context, 0, None)
		self.floats_4 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.h = name_type_map['Uint'](self.context, 0, None)
		self.floats_5 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.i = name_type_map['Uint'](self.context, 0, None)
		self.float = name_type_map['Float'](self.context, 0, None)
		self.fgm_name = name_type_map['Pointer'](self.context, 0, name_type_map['ZStringObfuscated'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'fgm_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None), (None, None)
		yield 'vec_0', name_type_map['Vector3F'], (0, None), (False, None), (None, None)
		yield 'vec_1', name_type_map['Vector3F'], (0, None), (False, None), (None, None)
		yield 'a', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vec_2', name_type_map['Vector3F'], (0, None), (False, None), (None, None)
		yield 'vec_3', name_type_map['Vector3F'], (0, None), (False, None), (None, None)
		yield 'vec_4', name_type_map['Vector3F'], (0, None), (False, None), (None, None)
		yield 'vec_5', name_type_map['Vector3F'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'd', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'floats_1', Array, (0, None, (2,), name_type_map['Float']), (False, None), (None, None)
		yield 'e', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'floats_2', Array, (0, None, (2,), name_type_map['Float']), (False, None), (None, None)
		yield 'f', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'floats_3', Array, (0, None, (8,), name_type_map['Float']), (False, None), (None, None)
		yield 'g', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'floats_4', Array, (0, None, (6,), name_type_map['Float']), (False, None), (None, None)
		yield 'h', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'floats_5', Array, (0, None, (20,), name_type_map['Float']), (False, None), (None, None)
		yield 'i', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'float', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'fgm_name', name_type_map['Pointer'], (0, name_type_map['ZStringObfuscated']), (False, None)
		yield 'vec_0', name_type_map['Vector3F'], (0, None), (False, None)
		yield 'vec_1', name_type_map['Vector3F'], (0, None), (False, None)
		yield 'a', name_type_map['Uint'], (0, None), (False, None)
		yield 'b', name_type_map['Uint'], (0, None), (False, None)
		yield 'vec_2', name_type_map['Vector3F'], (0, None), (False, None)
		yield 'vec_3', name_type_map['Vector3F'], (0, None), (False, None)
		yield 'vec_4', name_type_map['Vector3F'], (0, None), (False, None)
		yield 'vec_5', name_type_map['Vector3F'], (0, None), (False, None)
		yield 'c', name_type_map['Uint'], (0, None), (False, None)
		yield 'd', name_type_map['Uint'], (0, None), (False, None)
		yield 'floats_1', Array, (0, None, (2,), name_type_map['Float']), (False, None)
		yield 'e', name_type_map['Uint'], (0, None), (False, None)
		yield 'floats_2', Array, (0, None, (2,), name_type_map['Float']), (False, None)
		yield 'f', name_type_map['Uint'], (0, None), (False, None)
		yield 'floats_3', Array, (0, None, (8,), name_type_map['Float']), (False, None)
		yield 'g', name_type_map['Uint'], (0, None), (False, None)
		yield 'floats_4', Array, (0, None, (6,), name_type_map['Float']), (False, None)
		yield 'h', name_type_map['Uint'], (0, None), (False, None)
		yield 'floats_5', Array, (0, None, (20,), name_type_map['Float']), (False, None)
		yield 'i', name_type_map['Uint'], (0, None), (False, None)
		yield 'float', name_type_map['Float'], (0, None), (False, None)

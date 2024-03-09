from nifgen.formats.fgm.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class FgmHeader(MemStruct):

	"""
	# JWE, PZ - 64 bytes
	# JWE2 - 80 bytes
	# JWE2 patternset fgms seem to be in pool type 3, everything else in 2
	"""

	__name__ = 'FgmHeader'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self._texture_count = name_type_map['Uint64'](self.context, 0, None)
		self._attribute_count = name_type_map['Uint64'](self.context, 0, None)
		self._unk_0 = name_type_map['Uint64'](self.context, 0, None)
		self._unk_1 = name_type_map['Uint64'](self.context, 0, None)
		self._unk_2 = name_type_map['Uint64'](self.context, 0, None)
		self._unk_3 = name_type_map['Uint64'](self.context, 0, None)
		self.textures = name_type_map['ArrayPointer'](self.context, self._texture_count, name_type_map['TextureInfo'])
		self.attributes = name_type_map['ArrayPointer'](self.context, self._attribute_count, name_type_map['AttribInfo'])
		self.name_foreach_textures = name_type_map['ForEachPointer'](self.context, self.textures, name_type_map['TextureData'])
		self.value_foreach_attributes = name_type_map['ForEachPointer'](self.context, self.attributes, name_type_map['AttribData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield '_texture_count', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 15, None)
		yield '_texture_count', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 17, None)
		yield '_attribute_count', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 15, None)
		yield '_attribute_count', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.version >= 17, None)
		yield 'textures', name_type_map['ArrayPointer'], (None, name_type_map['TextureInfo']), (False, None), (None, None)
		yield 'attributes', name_type_map['ArrayPointer'], (None, name_type_map['AttribInfo']), (False, None), (None, None)
		yield 'name_foreach_textures', name_type_map['ForEachPointer'], (None, name_type_map['TextureData']), (False, None), (None, None)
		yield 'value_foreach_attributes', name_type_map['ForEachPointer'], (None, name_type_map['AttribData']), (False, None), (None, None)
		yield '_unk_0', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield '_unk_1', name_type_map['Uint64'], (0, None), (False, None), (None, None)
		yield '_unk_2', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.user_version.use_djb and (context.version == 20), None)
		yield '_unk_3', name_type_map['Uint64'], (0, None), (False, None), (lambda context: context.user_version.use_djb and (context.version == 20), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 15:
			yield '_texture_count', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 17:
			yield '_texture_count', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.version <= 15:
			yield '_attribute_count', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 17:
			yield '_attribute_count', name_type_map['Uint64'], (0, None), (False, None)
		yield 'textures', name_type_map['ArrayPointer'], (instance._texture_count, name_type_map['TextureInfo']), (False, None)
		yield 'attributes', name_type_map['ArrayPointer'], (instance._attribute_count, name_type_map['AttribInfo']), (False, None)
		yield 'name_foreach_textures', name_type_map['ForEachPointer'], (instance.textures, name_type_map['TextureData']), (False, None)
		yield 'value_foreach_attributes', name_type_map['ForEachPointer'], (instance.attributes, name_type_map['AttribData']), (False, None)
		yield '_unk_0', name_type_map['Uint64'], (0, None), (False, None)
		yield '_unk_1', name_type_map['Uint64'], (0, None), (False, None)
		if instance.context.user_version.use_djb and (instance.context.version == 20):
			yield '_unk_2', name_type_map['Uint64'], (0, None), (False, None)
			yield '_unk_3', name_type_map['Uint64'], (0, None), (False, None)

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class MaterialData(BaseStruct):

	__name__ = 'MaterialData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Shader.
		self.has_shader = name_type_map['Bool'](self.context, 0, None)

		# The shader name.
		self.shader_name = name_type_map['String'](self.context, 0, None)

		# Extra data associated with the shader. A value of -1 means the shader is the default implementation.
		self.shader_extra_data = name_type_map['Int'](self.context, 0, None)
		self.num_materials = name_type_map['Uint'](self.context, 0, None)

		# The name of the material.
		self.material_name = Array(self.context, 0, None, (0,), name_type_map['NiFixedString'])

		# Extra data associated with the material. A value of -1 means the material is the default implementation.
		self.material_extra_data = Array(self.context, 0, None, (0,), name_type_map['Int'])

		# The index of the currently active material.
		self.active_material = name_type_map['Int'].from_value(-1)

		# Cyanide extension (Blood Bowl).
		self.cyanide_unknown = name_type_map['Byte'].from_value(255)
		self.world_shift_unknown = name_type_map['Int'](self.context, 0, None)

		# Whether the materials for this object always needs to be updated before rendering with them.
		self.material_needs_update = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'has_shader', name_type_map['Bool'], (0, None), (False, None), (lambda context: 167772416 <= context.version <= 335609859, None)
		yield 'shader_name', name_type_map['String'], (0, None), (False, None), (lambda context: 167772416 <= context.version <= 335609859, True)
		yield 'shader_extra_data', name_type_map['Int'], (0, None), (False, None), (lambda context: 167772416 <= context.version <= 335609859, True)
		yield 'num_materials', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335675397, None)
		yield 'material_name', Array, (0, None, (None,), name_type_map['NiFixedString']), (False, None), (lambda context: context.version >= 335675397, None)
		yield 'material_extra_data', Array, (0, None, (None,), name_type_map['Int']), (False, None), (lambda context: context.version >= 335675397, None)
		yield 'active_material', name_type_map['Int'], (0, None), (False, -1), (lambda context: context.version >= 335675397, None)
		yield 'cyanide_unknown', name_type_map['Byte'], (0, None), (False, 255), (lambda context: 167903232 <= context.version <= 167903232 and context.user_version == 1, None)
		yield 'world_shift_unknown', name_type_map['Int'], (0, None), (False, None), (lambda context: 167968769 <= context.version <= 168034305, None)
		yield 'material_needs_update', name_type_map['Bool'], (0, None), (False, None), (lambda context: context.version >= 335675399, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 167772416 <= instance.context.version <= 335609859:
			yield 'has_shader', name_type_map['Bool'], (0, None), (False, None)
		if 167772416 <= instance.context.version <= 335609859 and instance.has_shader:
			yield 'shader_name', name_type_map['String'], (0, None), (False, None)
			yield 'shader_extra_data', name_type_map['Int'], (0, None), (False, None)
		if instance.context.version >= 335675397:
			yield 'num_materials', name_type_map['Uint'], (0, None), (False, None)
			yield 'material_name', Array, (0, None, (instance.num_materials,), name_type_map['NiFixedString']), (False, None)
			yield 'material_extra_data', Array, (0, None, (instance.num_materials,), name_type_map['Int']), (False, None)
			yield 'active_material', name_type_map['Int'], (0, None), (False, -1)
		if 167903232 <= instance.context.version <= 167903232 and instance.context.user_version == 1:
			yield 'cyanide_unknown', name_type_map['Byte'], (0, None), (False, 255)
		if 167968769 <= instance.context.version <= 168034305:
			yield 'world_shift_unknown', name_type_map['Int'], (0, None), (False, None)
		if instance.context.version >= 335675399:
			yield 'material_needs_update', name_type_map['Bool'], (0, None), (False, None)

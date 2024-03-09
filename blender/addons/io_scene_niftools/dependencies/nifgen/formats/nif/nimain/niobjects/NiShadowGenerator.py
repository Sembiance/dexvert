from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiShadowGenerator(NiObject):

	"""
	An NiShadowGenerator object is attached to an NiDynamicEffect object to inform the shadowing system that the effect produces shadows.
	"""

	__name__ = 'NiShadowGenerator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.name = name_type_map['String'].from_value('NiStandardShadowTechnique')
		self.flags = name_type_map['NiShadowGeneratorFlags'].from_value(987)
		self.num_shadow_casters = name_type_map['Uint'](self.context, 0, None)
		self.shadow_casters = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ref'])
		self.num_shadow_receivers = name_type_map['Uint'](self.context, 0, None)
		self.shadow_receivers = Array(self.context, 0, name_type_map['NiNode'], (0,), name_type_map['Ref'])
		self.target = name_type_map['Ptr'](self.context, 0, name_type_map['NiDynamicEffect'])
		self.depth_bias = name_type_map['Float'](self.context, 0, None)
		self.size_hint = name_type_map['Ushort'].from_value(1024)
		self.near_clipping_distance = name_type_map['Float'](self.context, 0, None)
		self.far_clipping_distance = name_type_map['Float'](self.context, 0, None)
		self.directional_light_frustum_width = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['String'], (0, None), (False, 'NiStandardShadowTechnique'), (None, None)
		yield 'flags', name_type_map['NiShadowGeneratorFlags'], (0, None), (False, 987), (None, None)
		yield 'num_shadow_casters', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'shadow_casters', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'num_shadow_receivers', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'shadow_receivers', Array, (0, name_type_map['NiNode'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiDynamicEffect']), (False, None), (None, None)
		yield 'depth_bias', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'size_hint', name_type_map['Ushort'], (0, None), (False, 1024), (None, None)
		yield 'near_clipping_distance', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335740935, None)
		yield 'far_clipping_distance', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335740935, None)
		yield 'directional_light_frustum_width', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 335740935, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['String'], (0, None), (False, 'NiStandardShadowTechnique')
		yield 'flags', name_type_map['NiShadowGeneratorFlags'], (0, None), (False, 987)
		yield 'num_shadow_casters', name_type_map['Uint'], (0, None), (False, None)
		yield 'shadow_casters', Array, (0, name_type_map['NiNode'], (instance.num_shadow_casters,), name_type_map['Ref']), (False, None)
		yield 'num_shadow_receivers', name_type_map['Uint'], (0, None), (False, None)
		yield 'shadow_receivers', Array, (0, name_type_map['NiNode'], (instance.num_shadow_receivers,), name_type_map['Ref']), (False, None)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiDynamicEffect']), (False, None)
		yield 'depth_bias', name_type_map['Float'], (0, None), (False, None)
		yield 'size_hint', name_type_map['Ushort'], (0, None), (False, 1024)
		if instance.context.version >= 335740935:
			yield 'near_clipping_distance', name_type_map['Float'], (0, None), (False, None)
			yield 'far_clipping_distance', name_type_map['Float'], (0, None), (False, None)
			yield 'directional_light_frustum_width', name_type_map['Float'], (0, None), (False, None)

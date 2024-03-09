from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiProperty import NiProperty


class NiStencilProperty(NiProperty):

	"""
	Allows control of stencil testing.
	"""

	__name__ = 'NiStencilProperty'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Property flags.
		self.flags = name_type_map['Ushort'](self.context, 0, None)

		# Enables or disables the stencil test.
		self.stencil_enabled = name_type_map['Byte'](self.context, 0, None)

		# Selects the compare mode function.
		self.stencil_function = name_type_map['StencilTestFunc'](self.context, 0, None)
		self.stencil_ref = name_type_map['Uint'](self.context, 0, None)

		# A bit mask. The default is 0xffffffff.
		self.stencil_mask = name_type_map['Uint'].from_value(4294967295)
		self.fail_action = name_type_map['StencilAction'](self.context, 0, None)
		self.z_fail_action = name_type_map['StencilAction'](self.context, 0, None)
		self.pass_action = name_type_map['StencilAction'](self.context, 0, None)

		# Used to enabled double sided faces. Default is 3 (DRAW_BOTH).
		self.draw_mode = name_type_map['StencilDrawMode'].DRAW_BOTH
		self.flags = name_type_map['StencilFlags'].from_value(19840)
		self.stencil_ref = name_type_map['Uint'](self.context, 0, None)

		# A bit mask. The default is 0xffffffff.
		self.stencil_mask = name_type_map['Uint'].from_value(4294967295)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'stencil_enabled', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'stencil_function', name_type_map['StencilTestFunc'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'stencil_ref', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'stencil_mask', name_type_map['Uint'], (0, None), (False, 4294967295), (lambda context: context.version <= 335544325, None)
		yield 'fail_action', name_type_map['StencilAction'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'z_fail_action', name_type_map['StencilAction'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'pass_action', name_type_map['StencilAction'], (0, None), (False, None), (lambda context: context.version <= 335544325, None)
		yield 'draw_mode', name_type_map['StencilDrawMode'], (0, None), (False, name_type_map['StencilDrawMode'].DRAW_BOTH), (lambda context: context.version <= 335544325, None)
		yield 'flags', name_type_map['StencilFlags'], (0, None), (False, 19840), (lambda context: context.version >= 335609859, None)
		yield 'stencil_ref', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version >= 335609859, None)
		yield 'stencil_mask', name_type_map['Uint'], (0, None), (False, 4294967295), (lambda context: context.version >= 335609859, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167772418:
			yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		if instance.context.version <= 335544325:
			yield 'stencil_enabled', name_type_map['Byte'], (0, None), (False, None)
			yield 'stencil_function', name_type_map['StencilTestFunc'], (0, None), (False, None)
			yield 'stencil_ref', name_type_map['Uint'], (0, None), (False, None)
			yield 'stencil_mask', name_type_map['Uint'], (0, None), (False, 4294967295)
			yield 'fail_action', name_type_map['StencilAction'], (0, None), (False, None)
			yield 'z_fail_action', name_type_map['StencilAction'], (0, None), (False, None)
			yield 'pass_action', name_type_map['StencilAction'], (0, None), (False, None)
			yield 'draw_mode', name_type_map['StencilDrawMode'], (0, None), (False, name_type_map['StencilDrawMode'].DRAW_BOTH)
		if instance.context.version >= 335609859:
			yield 'flags', name_type_map['StencilFlags'], (0, None), (False, 19840)
			yield 'stencil_ref', name_type_map['Uint'], (0, None), (False, None)
			yield 'stencil_mask', name_type_map['Uint'], (0, None), (False, 4294967295)

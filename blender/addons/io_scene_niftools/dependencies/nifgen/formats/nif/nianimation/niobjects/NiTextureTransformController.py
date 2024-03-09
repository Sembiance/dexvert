from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiFloatInterpController import NiFloatInterpController


class NiTextureTransformController(NiFloatInterpController):

	"""
	Used to animate a single member of an NiTextureTransform.
	NiInterpController::GetCtlrID() string formats:
	['%1-%2-TT_TRANSLATE_U', '%1-%2-TT_TRANSLATE_V', '%1-%2-TT_ROTATE', '%1-%2-TT_SCALE_U', '%1-%2-TT_SCALE_V']
	(Depending on "Operation" enumeration, %1 = Value of "Shader Map", %2 = Value of "Texture Slot")
	"""

	__name__ = 'NiTextureTransformController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Is the target map a shader map?
		self.shader_map = name_type_map['Bool'](self.context, 0, None)

		# The target texture slot.
		self.texture_slot = name_type_map['TexType'](self.context, 0, None)

		# Controls which aspect of the texture transform to modify.
		self.operation = name_type_map['TransformMember'](self.context, 0, None)
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['NiFloatData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shader_map', name_type_map['Bool'], (0, None), (False, None), (None, None)
		yield 'texture_slot', name_type_map['TexType'], (0, None), (False, None), (None, None)
		yield 'operation', name_type_map['TransformMember'], (0, None), (False, None), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None), (lambda context: context.version <= 167837799, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shader_map', name_type_map['Bool'], (0, None), (False, None)
		yield 'texture_slot', name_type_map['TexType'], (0, None), (False, None)
		yield 'operation', name_type_map['TransformMember'], (0, None), (False, None)
		if instance.context.version <= 167837799:
			yield 'data', name_type_map['Ref'], (0, name_type_map['NiFloatData']), (False, None)

from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiKeyframeController import NiKeyframeController


class NiTransformController(NiKeyframeController):

	"""
	NiTransformController replaces NiKeyframeController.
	"""

	__name__ = 'NiTransformController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Always 00 00 00 00?
		self.unknown_q_q_speed_integer = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unknown_q_q_speed_integer', name_type_map['Uint'], (0, None), (False, None), (lambda context: 335676695 <= context.version <= 335676695, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if 335676695 <= instance.context.version <= 335676695:
			yield 'unknown_q_q_speed_integer', name_type_map['Uint'], (0, None), (False, None)

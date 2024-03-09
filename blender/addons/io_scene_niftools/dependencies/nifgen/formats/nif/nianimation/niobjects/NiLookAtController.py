from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class NiLookAtController(NiTimeController):

	"""
	DEPRECATED (10.2), REMOVED (20.5)
	Replaced by NiTransformController and NiLookAtInterpolator.
	"""

	__name__ = 'NiLookAtController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.look_at_flags = name_type_map['LookAtFlags'](self.context, 0, None)
		self.look_at = name_type_map['Ptr'](self.context, 0, name_type_map['NiNode'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'look_at_flags', name_type_map['LookAtFlags'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'look_at', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 167837696:
			yield 'look_at_flags', name_type_map['LookAtFlags'], (0, None), (False, None)
		yield 'look_at', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None)

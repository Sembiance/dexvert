from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiKeyframeController import NiKeyframeController


class BSKeyframeController(NiKeyframeController):

	"""
	An extended keyframe controller.
	"""

	__name__ = 'BSKeyframeController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# A link to more keyframe data.
		self.data_2 = name_type_map['Ref'](self.context, 0, name_type_map['NiKeyframeData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data_2', name_type_map['Ref'], (0, name_type_map['NiKeyframeData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data_2', name_type_map['Ref'], (0, name_type_map['NiKeyframeData']), (False, None)

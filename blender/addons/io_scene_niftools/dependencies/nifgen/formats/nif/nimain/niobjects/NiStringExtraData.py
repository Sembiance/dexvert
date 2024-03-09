from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiExtraData import NiExtraData


class NiStringExtraData(NiExtraData):

	"""
	Extra data in the form of text.
	Used in various official or user-defined ways, e.g. preventing optimization on objects ("NiOptimizeKeep", "sgoKeep").
	"""

	__name__ = 'NiStringExtraData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The string.
		self.string_data = name_type_map['String'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'string_data', name_type_map['String'], (0, None), (False, None), (lambda context: context.version >= 67108864, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version >= 67108864:
			yield 'string_data', name_type_map['String'], (0, None), (False, None)

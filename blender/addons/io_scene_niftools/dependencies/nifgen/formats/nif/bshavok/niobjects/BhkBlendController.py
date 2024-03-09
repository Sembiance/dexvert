from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiTimeController import NiTimeController


class BhkBlendController(NiTimeController):

	"""
	Unknown. Is apparently only used in skeleton.nif files.
	"""

	__name__ = 'bhkBlendController'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Seems to be always zero.
		self.keys = name_type_map['Uint'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'keys', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'keys', name_type_map['Uint'], (0, None), (False, None)

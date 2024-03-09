from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiFloatData(NiObject):

	"""
	Wrapper for 1D (one-dimensional) floating point animation keys.
	"""

	__name__ = 'NiFloatData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The keys.
		self.data = name_type_map['KeyGroup'](self.context, 0, name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data', name_type_map['KeyGroup'], (0, name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data', name_type_map['KeyGroup'], (0, name_type_map['Float']), (False, None)

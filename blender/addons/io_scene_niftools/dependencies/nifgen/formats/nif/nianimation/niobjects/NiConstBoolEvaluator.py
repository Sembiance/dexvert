from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nianimation.niobjects.NiEvaluator import NiEvaluator


class NiConstBoolEvaluator(NiEvaluator):

	__name__ = 'NiConstBoolEvaluator'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# For floating point as boolean, 0.0 indicates false and 1.0 indicates true.
		self.value = name_type_map['Float'].from_value(-3.402823466e+38)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'value', name_type_map['Float'], (0, None), (False, -3.402823466e+38), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'value', name_type_map['Float'], (0, None), (False, -3.402823466e+38)

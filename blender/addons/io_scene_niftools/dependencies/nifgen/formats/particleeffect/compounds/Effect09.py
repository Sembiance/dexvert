from nifgen.array import Array
from nifgen.formats.particleeffect.compounds.Effect import Effect
from nifgen.formats.particleeffect.imports import name_type_map


class Effect09(Effect):

	"""
	32 bytes - PZ
	"""

	__name__ = 'Effect09'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'floats', Array, (0, None, (8,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'floats', Array, (0, None, (8,), name_type_map['Float']), (False, None)

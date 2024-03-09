from nifgen.array import Array
from nifgen.formats.particleeffect.compounds.Effect import Effect
from nifgen.formats.particleeffect.imports import name_type_map


class Effect15(Effect):

	"""
	32 bytes - PZ
	"""

	__name__ = 'Effect15'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.floats_1 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.flags = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.floats_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'floats_1', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, None)
		yield 'flags', Array, (0, None, (4,), name_type_map['Byte']), (False, None), (None, None)
		yield 'floats_2', Array, (0, None, (3,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'floats_1', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		yield 'flags', Array, (0, None, (4,), name_type_map['Byte']), (False, None)
		yield 'floats_2', Array, (0, None, (3,), name_type_map['Float']), (False, None)

from nifgen.formats.particleeffect.compounds.Effect import Effect
from nifgen.formats.particleeffect.imports import name_type_map


class Effect14(Effect):

	"""
	8 bytes - PZ
	probably indexing
	"""

	__name__ = 'Effect14'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.offset = name_type_map['Int'](self.context, 0, None)
		self.count = name_type_map['Int'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'offset', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'count', name_type_map['Int'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'offset', name_type_map['Int'], (0, None), (False, None)
		yield 'count', name_type_map['Int'], (0, None), (False, None)

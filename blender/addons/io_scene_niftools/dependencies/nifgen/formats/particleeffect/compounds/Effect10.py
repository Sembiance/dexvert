from nifgen.formats.particleeffect.compounds.Effect import Effect
from nifgen.formats.particleeffect.imports import name_type_map


class Effect10(Effect):

	"""
	48 bytes - PZ
	"""

	__name__ = 'Effect10'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zero_0 = name_type_map['Int64'](self.context, 0, None)
		self.u_0 = name_type_map['Short'](self.context, 0, None)
		self.u_1 = name_type_map['Short'](self.context, 0, None)
		self.zero_1 = name_type_map['Int'](self.context, 0, None)
		self.index = name_type_map['Int64'](self.context, 0, None)
		self.zero_2 = name_type_map['Int64'](self.context, 0, None)
		self.count = name_type_map['Int64'](self.context, 0, None)
		self.one_f = name_type_map['Float'](self.context, 0, None)
		self.zero_3 = name_type_map['Int'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zero_0', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'u_0', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'index', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'zero_2', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'count', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'one_f', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'zero_3', name_type_map['Int'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zero_0', name_type_map['Int64'], (0, None), (False, None)
		yield 'u_0', name_type_map['Short'], (0, None), (False, None)
		yield 'u_1', name_type_map['Short'], (0, None), (False, None)
		yield 'zero_1', name_type_map['Int'], (0, None), (False, None)
		yield 'index', name_type_map['Int64'], (0, None), (False, None)
		yield 'zero_2', name_type_map['Int64'], (0, None), (False, None)
		yield 'count', name_type_map['Int64'], (0, None), (False, None)
		yield 'one_f', name_type_map['Float'], (0, None), (False, None)
		yield 'zero_3', name_type_map['Int'], (0, None), (False, None)

from nifgen.array import Array
from nifgen.formats.particleeffect.compounds.Effect import Effect
from nifgen.formats.particleeffect.imports import name_type_map


class Effect07(Effect):

	"""
	might map the different effects per emitter?
	144 bytes - PZ
	+ 16 bytes for JWE2
	"""

	__name__ = 'Effect07'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zero_0 = name_type_map['Int64'](self.context, 0, None)
		self.a = name_type_map['Short'](self.context, 0, None)
		self.b = name_type_map['Short'](self.context, 0, None)
		self.ints = Array(self.context, 0, None, (0,), name_type_map['Int'])
		self.floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.c = name_type_map['Short'](self.context, 0, None)
		self.d = name_type_map['Short'](self.context, 0, None)
		self.one = name_type_map['Int64'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zero_0', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'a', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'ints', Array, (0, None, (30,), name_type_map['Int']), (False, None), (None, None)
		yield 'floats', Array, (0, None, (4,), name_type_map['Float']), (False, None), (lambda context: context.version >= 37, None)
		yield 'c', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'd', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'one', name_type_map['Int64'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zero_0', name_type_map['Int64'], (0, None), (False, None)
		yield 'a', name_type_map['Short'], (0, None), (False, None)
		yield 'b', name_type_map['Short'], (0, None), (False, None)
		yield 'ints', Array, (0, None, (30,), name_type_map['Int']), (False, None)
		if instance.context.version >= 37:
			yield 'floats', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		yield 'c', name_type_map['Short'], (0, None), (False, None)
		yield 'd', name_type_map['Short'], (0, None), (False, None)
		yield 'one', name_type_map['Int64'], (0, None), (False, None)

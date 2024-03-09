from nifgen.array import Array
from nifgen.formats.particleeffect.compounds.Effect import Effect
from nifgen.formats.particleeffect.imports import name_type_map


class Effect12(Effect):

	"""
	240 bytes - PZ
	"""

	__name__ = 'Effect12'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.zero_0 = name_type_map['Int64'](self.context, 0, None)
		self.u_0 = name_type_map['Short'](self.context, 0, None)
		self.u_1 = name_type_map['Short'](self.context, 0, None)
		self.zero_1 = name_type_map['Int'](self.context, 0, None)
		self.count_1 = name_type_map['Int64'](self.context, 0, None)
		self.zero_2 = name_type_map['Int64'](self.context, 0, None)
		self.count_2 = name_type_map['Int64'](self.context, 0, None)
		self.zeros = Array(self.context, 0, None, (0,), name_type_map['Int64'])
		self.floats_1 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.pi_rel = name_type_map['Float'](self.context, 0, None)
		self.floats_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.ints = Array(self.context, 0, None, (0,), name_type_map['Int'])
		self.floats_3 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.bytes = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.float = name_type_map['Float'](self.context, 0, None)
		self.ints_2 = Array(self.context, 0, None, (0,), name_type_map['Int'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'zero_0', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'u_0', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'u_1', name_type_map['Short'], (0, None), (False, None), (None, None)
		yield 'zero_1', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'count_1', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'zero_2', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'count_2', name_type_map['Int64'], (0, None), (False, None), (None, None)
		yield 'zeros', Array, (0, None, (7,), name_type_map['Int64']), (False, None), (None, None)
		yield 'floats_1', Array, (0, None, (4,), name_type_map['Float']), (False, None), (None, None)
		yield 'pi_rel', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'floats_2', Array, (0, None, (5,), name_type_map['Float']), (False, None), (None, None)
		yield 'ints', Array, (0, None, (8,), name_type_map['Int']), (False, None), (None, None)
		yield 'floats_3', Array, (0, None, (10,), name_type_map['Float']), (False, None), (None, None)
		yield 'bytes', Array, (0, None, (16,), name_type_map['Byte']), (False, None), (None, None)
		yield 'float', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'ints_2', Array, (0, None, (3,), name_type_map['Int']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'zero_0', name_type_map['Int64'], (0, None), (False, None)
		yield 'u_0', name_type_map['Short'], (0, None), (False, None)
		yield 'u_1', name_type_map['Short'], (0, None), (False, None)
		yield 'zero_1', name_type_map['Int'], (0, None), (False, None)
		yield 'count_1', name_type_map['Int64'], (0, None), (False, None)
		yield 'zero_2', name_type_map['Int64'], (0, None), (False, None)
		yield 'count_2', name_type_map['Int64'], (0, None), (False, None)
		yield 'zeros', Array, (0, None, (7,), name_type_map['Int64']), (False, None)
		yield 'floats_1', Array, (0, None, (4,), name_type_map['Float']), (False, None)
		yield 'pi_rel', name_type_map['Float'], (0, None), (False, None)
		yield 'floats_2', Array, (0, None, (5,), name_type_map['Float']), (False, None)
		yield 'ints', Array, (0, None, (8,), name_type_map['Int']), (False, None)
		yield 'floats_3', Array, (0, None, (10,), name_type_map['Float']), (False, None)
		yield 'bytes', Array, (0, None, (16,), name_type_map['Byte']), (False, None)
		yield 'float', name_type_map['Float'], (0, None), (False, None)
		yield 'ints_2', Array, (0, None, (3,), name_type_map['Int']), (False, None)

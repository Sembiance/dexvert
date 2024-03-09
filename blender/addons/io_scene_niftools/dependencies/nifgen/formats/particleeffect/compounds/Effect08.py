from nifgen.array import Array
from nifgen.formats.particleeffect.compounds.Effect import Effect
from nifgen.formats.particleeffect.imports import name_type_map


class Effect08(Effect):

	"""
	96 bytes - PZ
	"""

	__name__ = 'Effect08'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.floats = Array(self.context, 0, None, (0,), name_type_map['Float'])
		self.minus_1 = name_type_map['Int'](self.context, 0, None)
		self.z_2 = name_type_map['Int'](self.context, 0, None)
		self.z_3 = name_type_map['Int'](self.context, 0, None)
		self.pi = name_type_map['Float'](self.context, 0, None)
		self.floats_2 = Array(self.context, 0, None, (0,), name_type_map['Float'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'floats', Array, (0, None, (15,), name_type_map['Float']), (False, None), (None, None)
		yield 'minus_1', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'z_2', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'z_3', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'pi', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'floats_2', Array, (0, None, (5,), name_type_map['Float']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'floats', Array, (0, None, (15,), name_type_map['Float']), (False, None)
		yield 'minus_1', name_type_map['Int'], (0, None), (False, None)
		yield 'z_2', name_type_map['Int'], (0, None), (False, None)
		yield 'z_3', name_type_map['Int'], (0, None), (False, None)
		yield 'pi', name_type_map['Float'], (0, None), (False, None)
		yield 'floats_2', Array, (0, None, (5,), name_type_map['Float']), (False, None)

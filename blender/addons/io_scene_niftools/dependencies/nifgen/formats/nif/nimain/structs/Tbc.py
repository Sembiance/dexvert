from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Tbc(BaseStruct):

	"""
	Tension, bias, continuity.
	"""

	__name__ = 'TBC'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Tension.
		self.t = name_type_map['Float'](self.context, 0, None)

		# Bias.
		self.b = name_type_map['Float'](self.context, 0, None)

		# Continuity.
		self.c = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 't', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'c', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 't', name_type_map['Float'], (0, None), (False, None)
		yield 'b', name_type_map['Float'], (0, None), (False, None)
		yield 'c', name_type_map['Float'], (0, None), (False, None)

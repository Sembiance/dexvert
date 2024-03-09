from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Key(BaseStruct):

	"""
	A generic key with support for interpolation. Type 1 is normal linear interpolation, type 2 has forward and backward tangents, and type 3 has tension, bias and continuity arguments. Note that color4 and byte always seem to be of type 1.
	"""

	__name__ = 'Key'


	def __init__(self, context, arg=0, template=None, set_default=True):
		if template is None:
			raise TypeError(f'{type(self).__name__} requires template is not None')
		super().__init__(context, arg, template, set_default=False)

		# Time of the key.
		self.time = name_type_map['Float'](self.context, 0, None)

		# The key value.
		self.value = self.template(self.context, 0, None)

		# Key forward tangent.
		self.forward = self.template(self.context, 0, None)

		# The key backward tangent.
		self.backward = self.template(self.context, 0, None)

		# The TBC of the key.
		self.tbc = name_type_map['Tbc'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'time', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'value', None, (0, None), (False, None), (None, None)
		yield 'forward', None, (0, None), (False, None), (None, True)
		yield 'backward', None, (0, None), (False, None), (None, True)
		yield 'tbc', name_type_map['Tbc'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'time', name_type_map['Float'], (0, None), (False, None)
		yield 'value', instance.template, (0, None), (False, None)
		if instance.arg == 2:
			yield 'forward', instance.template, (0, None), (False, None)
			yield 'backward', instance.template, (0, None), (False, None)
		if instance.arg == 3:
			yield 'tbc', name_type_map['Tbc'], (0, None), (False, None)

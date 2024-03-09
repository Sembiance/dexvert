from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class KeyGroup(BaseStruct):

	"""
	Array of vector keys (anything that can be interpolated, except rotations).
	"""

	__name__ = 'KeyGroup'


	def __init__(self, context, arg=0, template=None, set_default=True):
		if template is None:
			raise TypeError(f'{type(self).__name__} requires template is not None')
		super().__init__(context, arg, template, set_default=False)

		# Number of keys in the array.
		self.num_keys = name_type_map['Uint'](self.context, 0, None)

		# The key type.
		self.interpolation = name_type_map['KeyType'](self.context, 0, None)

		# The keys.
		self.keys = Array(self.context, self.interpolation, self.template, (0,), name_type_map['Key'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_keys', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'interpolation', name_type_map['KeyType'], (0, None), (False, None), (None, True)
		yield 'keys', Array, (None, None, (None,), name_type_map['Key']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_keys', name_type_map['Uint'], (0, None), (False, None)
		if instance.num_keys != 0:
			yield 'interpolation', name_type_map['KeyType'], (0, None), (False, None)
		yield 'keys', Array, (instance.interpolation, instance.template, (instance.num_keys,), name_type_map['Key']), (False, None)

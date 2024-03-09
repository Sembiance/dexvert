from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class QuatKey(BaseStruct):

	"""
	A special version of the key type used for quaternions. Never has tangents. #T# should always be Quaternion.
	"""

	__name__ = 'QuatKey'


	def __init__(self, context, arg=0, template=None, set_default=True):
		if template is None:
			raise TypeError(f'{type(self).__name__} requires template is not None')
		super().__init__(context, arg, template, set_default=False)

		# Time the key applies.
		self.time = name_type_map['Float'](self.context, 0, None)

		# Value of the key.
		self.value = self.template(self.context, 0, None)

		# The TBC of the key.
		self.tbc = name_type_map['Tbc'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'time', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version <= 167837696, None)
		yield 'time', name_type_map['Float'], (0, None), (False, None), (lambda context: context.version >= 167837802, True)
		yield 'value', None, (0, None), (False, None), (None, True)
		yield 'tbc', name_type_map['Tbc'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.version <= 167837696:
			yield 'time', name_type_map['Float'], (0, None), (False, None)
		if instance.context.version >= 167837802 and instance.arg != 4:
			yield 'time', name_type_map['Float'], (0, None), (False, None)
		if instance.arg != 4:
			yield 'value', instance.template, (0, None), (False, None)
		if instance.arg == 3:
			yield 'tbc', name_type_map['Tbc'], (0, None), (False, None)

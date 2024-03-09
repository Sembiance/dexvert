from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Triangle(BaseStruct):

	"""
	List of three vertex indices.
	"""

	__name__ = 'Triangle'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# First vertex index.
		self.v_1 = name_type_map['Ushort'](self.context, 0, None)

		# Second vertex index.
		self.v_2 = name_type_map['Ushort'](self.context, 0, None)

		# Third vertex index.
		self.v_3 = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'v_1', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'v_2', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'v_3', name_type_map['Ushort'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'v_1', name_type_map['Ushort'], (0, None), (False, None)
		yield 'v_2', name_type_map['Ushort'], (0, None), (False, None)
		yield 'v_3', name_type_map['Ushort'], (0, None), (False, None)

from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class Matrix22(BaseStruct):

	"""
	A 2x2 matrix of float values.  Stored in OpenGL column-major format.
	"""

	__name__ = 'Matrix22'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Member 1,1 (top left)
		self.m_11 = name_type_map['Float'].from_value(1.0)

		# Member 2,1 (bottom left)
		self.m_21 = name_type_map['Float'].from_value(0.0)

		# Member 1,2 (top right)
		self.m_12 = name_type_map['Float'].from_value(0.0)

		# Member 2,2 (bottom right)
		self.m_22 = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'm_11', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'm_21', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_12', name_type_map['Float'], (0, None), (False, 0.0), (None, None)
		yield 'm_22', name_type_map['Float'], (0, None), (False, 1.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'm_11', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'm_21', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_12', name_type_map['Float'], (0, None), (False, 0.0)
		yield 'm_22', name_type_map['Float'], (0, None), (False, 1.0)

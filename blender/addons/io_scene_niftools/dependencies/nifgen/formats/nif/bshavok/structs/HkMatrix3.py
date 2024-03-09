from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HkMatrix3(BaseStruct):

	"""
	A 3x3 Havok matrix stored in 4x3 due to memory alignment.
	"""

	__name__ = 'hkMatrix3'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.m_11 = name_type_map['Float'].from_value(1.0)
		self.m_12 = name_type_map['Float'](self.context, 0, None)
		self.m_13 = name_type_map['Float'](self.context, 0, None)

		# Unused
		self.m_14 = name_type_map['Float'](self.context, 0, None)
		self.m_21 = name_type_map['Float'](self.context, 0, None)
		self.m_22 = name_type_map['Float'].from_value(1.0)
		self.m_23 = name_type_map['Float'](self.context, 0, None)

		# Unused
		self.m_24 = name_type_map['Float'](self.context, 0, None)
		self.m_31 = name_type_map['Float'](self.context, 0, None)
		self.m_32 = name_type_map['Float'](self.context, 0, None)
		self.m_33 = name_type_map['Float'].from_value(1.0)

		# Unused
		self.m_34 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'm_11', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'm_12', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_13', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_14', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_21', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_22', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'm_23', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_24', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_31', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_32', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'm_33', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'm_34', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'm_11', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'm_12', name_type_map['Float'], (0, None), (False, None)
		yield 'm_13', name_type_map['Float'], (0, None), (False, None)
		yield 'm_14', name_type_map['Float'], (0, None), (False, None)
		yield 'm_21', name_type_map['Float'], (0, None), (False, None)
		yield 'm_22', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'm_23', name_type_map['Float'], (0, None), (False, None)
		yield 'm_24', name_type_map['Float'], (0, None), (False, None)
		yield 'm_31', name_type_map['Float'], (0, None), (False, None)
		yield 'm_32', name_type_map['Float'], (0, None), (False, None)
		yield 'm_33', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'm_34', name_type_map['Float'], (0, None), (False, None)

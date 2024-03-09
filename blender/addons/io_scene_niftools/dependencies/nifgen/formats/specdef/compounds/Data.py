from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.specdef.imports import name_type_map


class Data(MemStruct):

	"""
	#ARG# is dtype
	todo - enum, grab, implement, fetch
	"""

	__name__ = 'Data'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.dtype = name_type_map['ReferenceToObjectData'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'dtype', name_type_map['BooleanData'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Int8Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Int16Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Int32Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Int64Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Uint8Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Uint16Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Uint32Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Uint64Data'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['FloatData'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['StringData'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Vector2'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['Vector3'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['ArrayData'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['ChildSpecData'], (0, None), (False, None), (None, True)
		yield 'dtype', name_type_map['ReferenceToObjectData'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.arg == 0:
			yield 'dtype', name_type_map['BooleanData'], (0, None), (False, None)
		if instance.arg == 1:
			yield 'dtype', name_type_map['Int8Data'], (0, None), (False, None)
		if instance.arg == 2:
			yield 'dtype', name_type_map['Int16Data'], (0, None), (False, None)
		if instance.arg == 3:
			yield 'dtype', name_type_map['Int32Data'], (0, None), (False, None)
		if instance.arg == 4:
			yield 'dtype', name_type_map['Int64Data'], (0, None), (False, None)
		if instance.arg == 5:
			yield 'dtype', name_type_map['Uint8Data'], (0, None), (False, None)
		if instance.arg == 6:
			yield 'dtype', name_type_map['Uint16Data'], (0, None), (False, None)
		if instance.arg == 7:
			yield 'dtype', name_type_map['Uint32Data'], (0, None), (False, None)
		if instance.arg == 8:
			yield 'dtype', name_type_map['Uint64Data'], (0, None), (False, None)
		if instance.arg == 9:
			yield 'dtype', name_type_map['FloatData'], (0, None), (False, None)
		if instance.arg == 10:
			yield 'dtype', name_type_map['StringData'], (0, None), (False, None)
		if instance.arg == 11:
			yield 'dtype', name_type_map['Vector2'], (0, None), (False, None)
		if instance.arg == 12:
			yield 'dtype', name_type_map['Vector3'], (0, None), (False, None)
		if instance.arg == 13:
			yield 'dtype', name_type_map['ArrayData'], (0, None), (False, None)
		if instance.arg == 14:
			yield 'dtype', name_type_map['ChildSpecData'], (0, None), (False, None)
		if instance.arg == 15:
			yield 'dtype', name_type_map['ReferenceToObjectData'], (0, None), (False, None)

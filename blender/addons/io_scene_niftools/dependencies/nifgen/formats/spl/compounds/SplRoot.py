from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct
from nifgen.formats.spl.imports import name_type_map


class SplRoot(MemStruct):

	"""
	JWE2: 16 bytes
	"""

	__name__ = 'SplRoot'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.count = name_type_map['Ushort'](self.context, 0, None)
		self.sixteen = name_type_map['Ubyte'].from_value(16)
		self.one = name_type_map['Ubyte'].from_value(1)

		# total length of the interpolated curve, cf blender Spline.calc_length()
		self.length = name_type_map['Float'](self.context, 0, None)
		self.spline_data = name_type_map['Pointer'](self.context, self.count, name_type_map['SplData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'spline_data', name_type_map['Pointer'], (None, name_type_map['SplData']), (False, None), (None, None)
		yield 'count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'sixteen', name_type_map['Ubyte'], (0, None), (False, 16), (None, None)
		yield 'one', name_type_map['Ubyte'], (0, None), (False, 1), (None, None)
		yield 'length', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'spline_data', name_type_map['Pointer'], (instance.count, name_type_map['SplData']), (False, None)
		yield 'count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'sixteen', name_type_map['Ubyte'], (0, None), (False, 16)
		yield 'one', name_type_map['Ubyte'], (0, None), (False, 1)
		yield 'length', name_type_map['Float'], (0, None), (False, None)

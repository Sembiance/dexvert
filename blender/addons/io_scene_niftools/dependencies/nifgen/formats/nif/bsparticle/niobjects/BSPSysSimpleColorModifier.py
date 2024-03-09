from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSPSysSimpleColorModifier(NiPSysModifier):

	"""
	Bethesda-specific particle modifier.
	"""

	__name__ = 'BSPSysSimpleColorModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.fade_in_percent = name_type_map['Float'].from_value(0.1)
		self.fade_out_percent = name_type_map['Float'].from_value(0.9)
		self.color_1_end_percent = name_type_map['Float'](self.context, 0, None)
		self.color_1_start_percent = name_type_map['Float'](self.context, 0, None)
		self.color_2_end_percent = name_type_map['Float'](self.context, 0, None)
		self.color_2_start_percent = name_type_map['Float'].from_value(1.0)
		self.colors = Array(self.context, 0, None, (0,), name_type_map['Color4'])
		self.unknown_shorts = Array(self.context, 0, None, (0,), name_type_map['Ushort'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'fade_in_percent', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'fade_out_percent', name_type_map['Float'], (0, None), (False, 0.9), (None, None)
		yield 'color_1_end_percent', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'color_1_start_percent', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'color_2_end_percent', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'color_2_start_percent', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'colors', Array, (0, None, (3,), name_type_map['Color4']), (False, None), (None, None)
		yield 'unknown_shorts', Array, (0, None, (26,), name_type_map['Ushort']), (False, None), (lambda context: context.bs_header.bs_version == 155, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'fade_in_percent', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'fade_out_percent', name_type_map['Float'], (0, None), (False, 0.9)
		yield 'color_1_end_percent', name_type_map['Float'], (0, None), (False, None)
		yield 'color_1_start_percent', name_type_map['Float'], (0, None), (False, None)
		yield 'color_2_end_percent', name_type_map['Float'], (0, None), (False, None)
		yield 'color_2_start_percent', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'colors', Array, (0, None, (3,), name_type_map['Color4']), (False, None)
		if instance.context.bs_header.bs_version == 155:
			yield 'unknown_shorts', Array, (0, None, (26,), name_type_map['Ushort']), (False, None)

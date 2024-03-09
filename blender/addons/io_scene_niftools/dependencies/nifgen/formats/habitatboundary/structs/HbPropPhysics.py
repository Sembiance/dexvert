from nifgen.formats.habitatboundary.imports import name_type_map
from nifgen.formats.ovl_base.compounds.MemStruct import MemStruct


class HbPropPhysics(MemStruct):

	__name__ = 'HB_PropPhysics'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Affects selection area above object.
		self.pad_top = name_type_map['Float'](self.context, 0, None)

		# Z offset of box from prop object.
		self.z_pos = name_type_map['Float'](self.context, 0, None)

		# Affects selection area and rejects barrier placement inside area.
		self.half_width = name_type_map['Float'](self.context, 0, None)

		# Affects selection area below object.
		self.pad_bottom = name_type_map['Float'](self.context, 0, None)

		# Affects selection area and rejects barrier placement inside area.
		self.half_depth = name_type_map['Float'](self.context, 0, None)

		# Unknown effect. Possibly vertical offset of box, yet testing was inconclusive.
		self.u_6 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pad_top', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'z_pos', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'half_width', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'pad_bottom', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'half_depth', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'u_6', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pad_top', name_type_map['Float'], (0, None), (False, None)
		yield 'z_pos', name_type_map['Float'], (0, None), (False, None)
		yield 'half_width', name_type_map['Float'], (0, None), (False, None)
		yield 'pad_bottom', name_type_map['Float'], (0, None), (False, None)
		yield 'half_depth', name_type_map['Float'], (0, None), (False, None)
		yield 'u_6', name_type_map['Float'], (0, None), (False, None)

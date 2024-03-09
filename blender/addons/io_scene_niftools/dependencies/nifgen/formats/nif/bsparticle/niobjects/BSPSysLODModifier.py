from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class BSPSysLODModifier(NiPSysModifier):

	__name__ = 'BSPSysLODModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.lod_begin_distance = name_type_map['Float'].from_value(0.1)
		self.lod_end_distance = name_type_map['Float'].from_value(0.7)
		self.end_emit_scale = name_type_map['Float'].from_value(0.2)
		self.end_size = name_type_map['Float'].from_value(1.0)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'lod_begin_distance', name_type_map['Float'], (0, None), (False, 0.1), (None, None)
		yield 'lod_end_distance', name_type_map['Float'], (0, None), (False, 0.7), (None, None)
		yield 'end_emit_scale', name_type_map['Float'], (0, None), (False, 0.2), (None, None)
		yield 'end_size', name_type_map['Float'], (0, None), (False, 1.0), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'lod_begin_distance', name_type_map['Float'], (0, None), (False, 0.1)
		yield 'lod_end_distance', name_type_map['Float'], (0, None), (False, 0.7)
		yield 'end_emit_scale', name_type_map['Float'], (0, None), (False, 0.2)
		yield 'end_size', name_type_map['Float'], (0, None), (False, 1.0)

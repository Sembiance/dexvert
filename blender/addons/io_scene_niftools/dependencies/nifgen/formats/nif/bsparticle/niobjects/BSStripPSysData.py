from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysData import NiPSysData


class BSStripPSysData(NiPSysData):

	"""
	Bethesda-Specific (mesh?) Particle System Data.
	"""

	__name__ = 'BSStripPSysData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.max_point_count = name_type_map['Ushort'](self.context, 0, None)
		self.start_cap_size = name_type_map['Float'](self.context, 0, None)
		self.end_cap_size = name_type_map['Float'](self.context, 0, None)
		self.do_z_prepass = name_type_map['Bool'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'max_point_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'start_cap_size', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'end_cap_size', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'do_z_prepass', name_type_map['Bool'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'max_point_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'start_cap_size', name_type_map['Float'], (0, None), (False, None)
		yield 'end_cap_size', name_type_map['Float'], (0, None), (False, None)
		yield 'do_z_prepass', name_type_map['Bool'], (0, None), (False, None)

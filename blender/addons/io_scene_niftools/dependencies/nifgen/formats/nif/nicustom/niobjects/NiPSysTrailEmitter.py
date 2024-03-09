from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysSphereEmitter import NiPSysSphereEmitter


class NiPSysTrailEmitter(NiPSysSphereEmitter):

	"""
	Guild 2-Specific node
	"""

	__name__ = 'NiPSysTrailEmitter'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.trail_life_span = name_type_map['Float'](self.context, 0, None)
		self.trail_life_span_var = name_type_map['Float'](self.context, 0, None)
		self.num_trails = name_type_map['Int'](self.context, 0, None)
		self.gravity_force = name_type_map['Float'](self.context, 0, None)
		self.gravity_dir = name_type_map['Vector3'](self.context, 0, None)
		self.turbulence = name_type_map['Float'](self.context, 0, None)
		self.repeat_time = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'trail_life_span', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'trail_life_span_var', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'num_trails', name_type_map['Int'], (0, None), (False, None), (None, None)
		yield 'gravity_force', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'gravity_dir', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'repeat_time', name_type_map['Float'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'trail_life_span', name_type_map['Float'], (0, None), (False, None)
		yield 'trail_life_span_var', name_type_map['Float'], (0, None), (False, None)
		yield 'num_trails', name_type_map['Int'], (0, None), (False, None)
		yield 'gravity_force', name_type_map['Float'], (0, None), (False, None)
		yield 'gravity_dir', name_type_map['Vector3'], (0, None), (False, None)
		yield 'turbulence', name_type_map['Float'], (0, None), (False, None)
		yield 'repeat_time', name_type_map['Float'], (0, None), (False, None)

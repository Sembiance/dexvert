from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiNode import NiNode


class BSMasterParticleSystem(NiNode):

	"""
	Bethesda-Specific particle system.
	"""

	__name__ = 'BSMasterParticleSystem'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.max_emitter_objects = name_type_map['Ushort'].from_value(20)
		self.num_particle_systems = name_type_map['Uint'](self.context, 0, None)
		self.particle_systems = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'max_emitter_objects', name_type_map['Ushort'], (0, None), (False, 20), (None, None)
		yield 'num_particle_systems', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'particle_systems', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'max_emitter_objects', name_type_map['Ushort'], (0, None), (False, 20)
		yield 'num_particle_systems', name_type_map['Uint'], (0, None), (False, None)
		yield 'particle_systems', Array, (0, name_type_map['NiAVObject'], (instance.num_particle_systems,), name_type_map['Ref']), (False, None)

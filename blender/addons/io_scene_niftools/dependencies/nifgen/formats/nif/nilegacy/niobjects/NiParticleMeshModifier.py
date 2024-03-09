from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiParticleModifier import NiParticleModifier


class NiParticleMeshModifier(NiParticleModifier):

	"""
	LEGACY (pre-10.1) particle modifier.
	"""

	__name__ = 'NiParticleMeshModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_particle_meshes = name_type_map['Uint'](self.context, 0, None)
		self.particle_meshes = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_particle_meshes', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'particle_meshes', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_particle_meshes', name_type_map['Uint'], (0, None), (False, None)
		yield 'particle_meshes', Array, (0, name_type_map['NiAVObject'], (instance.num_particle_meshes,), name_type_map['Ref']), (False, None)

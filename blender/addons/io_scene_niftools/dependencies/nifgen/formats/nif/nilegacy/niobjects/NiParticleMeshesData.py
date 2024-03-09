from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nilegacy.niobjects.NiRotatingParticlesData import NiRotatingParticlesData


class NiParticleMeshesData(NiRotatingParticlesData):

	"""
	LEGACY (pre-10.1). Particle meshes data.
	"""

	__name__ = 'NiParticleMeshesData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.container_node = name_type_map['Ref'](self.context, 0, name_type_map['NiNode'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'container_node', name_type_map['Ref'], (0, name_type_map['NiNode']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'container_node', name_type_map['Ref'], (0, name_type_map['NiNode']), (False, None)

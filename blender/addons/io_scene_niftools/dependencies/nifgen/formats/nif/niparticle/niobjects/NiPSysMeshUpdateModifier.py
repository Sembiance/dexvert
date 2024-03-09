from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.niparticle.niobjects.NiPSysModifier import NiPSysModifier


class NiPSysMeshUpdateModifier(NiPSysModifier):

	"""
	Particle modifier that updates mesh particles using the age of each particle.
	"""

	__name__ = 'NiPSysMeshUpdateModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_meshes = name_type_map['Uint'](self.context, 0, None)
		self.meshes = Array(self.context, 0, name_type_map['NiAVObject'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_meshes', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'meshes', Array, (0, name_type_map['NiAVObject'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_meshes', name_type_map['Uint'], (0, None), (False, None)
		yield 'meshes', Array, (0, name_type_map['NiAVObject'], (instance.num_meshes,), name_type_map['Ref']), (False, None)

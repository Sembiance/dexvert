from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nipsparticle.niobjects.NiPSSimulatorStep import NiPSSimulatorStep


class NiPSSimulatorCollidersStep(NiPSSimulatorStep):

	"""
	Encapsulates a floodgate kernel that simulates particle colliders.
	"""

	__name__ = 'NiPSSimulatorCollidersStep'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_colliders = name_type_map['Uint'](self.context, 0, None)

		# The colliders affecting the particle system.
		self.colliders = Array(self.context, 0, name_type_map['NiPSCollider'], (0,), name_type_map['Ref'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_colliders', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'colliders', Array, (0, name_type_map['NiPSCollider'], (None,), name_type_map['Ref']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_colliders', name_type_map['Uint'], (0, None), (False, None)
		yield 'colliders', Array, (0, name_type_map['NiPSCollider'], (instance.num_colliders,), name_type_map['Ref']), (False, None)

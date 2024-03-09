from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiCollisionObject import NiCollisionObject


class NiCollisionData(NiCollisionObject):

	"""
	Collision box.
	"""

	__name__ = 'NiCollisionData'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.propagation_mode = name_type_map['PropagationMode'].PROPAGATE_ALWAYS
		self.collision_mode = name_type_map['CollisionMode'].NOTEST

		# Use Alternate Bounding Volume.
		self.use_abv = name_type_map['Byte'](self.context, 0, None)
		self.bounding_volume = name_type_map['BoundingVolume'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'propagation_mode', name_type_map['PropagationMode'], (0, None), (False, name_type_map['PropagationMode'].PROPAGATE_ALWAYS), (None, None)
		yield 'collision_mode', name_type_map['CollisionMode'], (0, None), (False, name_type_map['CollisionMode'].NOTEST), (lambda context: context.version >= 167837696, None)
		yield 'use_abv', name_type_map['Byte'], (0, None), (False, None), (None, None)
		yield 'bounding_volume', name_type_map['BoundingVolume'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'propagation_mode', name_type_map['PropagationMode'], (0, None), (False, name_type_map['PropagationMode'].PROPAGATE_ALWAYS)
		if instance.context.version >= 167837696:
			yield 'collision_mode', name_type_map['CollisionMode'], (0, None), (False, name_type_map['CollisionMode'].NOTEST)
		yield 'use_abv', name_type_map['Byte'], (0, None), (False, None)
		if instance.use_abv == 1:
			yield 'bounding_volume', name_type_map['BoundingVolume'], (0, None), (False, None)

	def apply_scale(self, scale):
		super().apply_scale(scale)
		if hasattr(self, 'bounding_volume'):
			self.bounding_volume.apply_scale(scale)

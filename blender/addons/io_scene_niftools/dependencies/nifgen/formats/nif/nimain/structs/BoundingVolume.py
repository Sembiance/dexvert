from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class BoundingVolume(BaseStruct):

	__name__ = 'BoundingVolume'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Type of collision data.
		self.collision_type = name_type_map['BoundVolumeType'](self.context, 0, None)
		self.sphere = name_type_map['NiBound'](self.context, 0, None)
		self.box = name_type_map['BoxBV'](self.context, 0, None)
		self.capsule = name_type_map['CapsuleBV'](self.context, 0, None)
		self.half_space = name_type_map['HalfSpaceBV'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'collision_type', name_type_map['BoundVolumeType'], (0, None), (False, None), (None, None)
		yield 'sphere', name_type_map['NiBound'], (0, None), (False, None), (None, True)
		yield 'box', name_type_map['BoxBV'], (0, None), (False, None), (None, True)
		yield 'capsule', name_type_map['CapsuleBV'], (0, None), (False, None), (None, True)
		yield 'union_bv', name_type_map['UnionBV'], (0, None), (False, None), (None, True)
		yield 'half_space', name_type_map['HalfSpaceBV'], (0, None), (False, None), (None, True)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'collision_type', name_type_map['BoundVolumeType'], (0, None), (False, None)
		if instance.collision_type == 0:
			yield 'sphere', name_type_map['NiBound'], (0, None), (False, None)
		if instance.collision_type == 1:
			yield 'box', name_type_map['BoxBV'], (0, None), (False, None)
		if instance.collision_type == 2:
			yield 'capsule', name_type_map['CapsuleBV'], (0, None), (False, None)
		if instance.collision_type == 4:
			yield 'union_bv', name_type_map['UnionBV'], (0, None), (False, None)
		if instance.collision_type == 5:
			yield 'half_space', name_type_map['HalfSpaceBV'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor on data.

		:param scale: The scale factor."""
		if hasattr(self, "sphere"):
			self.sphere.apply_scale(scale)
		if hasattr(self, "box"):
			self.box.center *= scale
			self.box.extent *= scale
		if hasattr(self, "capsule"):
			self.capsule.center *= scale
			self.capsule.origin *= scale
			self.capsule.extent *= scale
			self.capsule.radius *= scale
		if hasattr(self, "half_space"):
			self.half_space.plane.constant *= scale
			self.half_space.center *= scale


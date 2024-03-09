from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class NiBound(BaseStruct):

	"""
	A sphere.
	"""

	__name__ = 'NiBound'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The sphere's center.
		self.center = name_type_map['Vector3'](self.context, 0, None)

		# The sphere's radius.
		self.radius = name_type_map['Float'](self.context, 0, None)
		self.div_2_aabb = name_type_map['NiBoundAABB'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'center', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'div_2_aabb', name_type_map['NiBoundAABB'], (0, None), (False, None), (lambda context: 335740937 <= context.version <= 335740937 and (context.user_version == 131072) or (context.user_version == 196608), None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'center', name_type_map['Vector3'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		if 335740937 <= instance.context.version <= 335740937 and (instance.context.user_version == 131072) or (instance.context.user_version == 196608):
			yield 'div_2_aabb', name_type_map['NiBoundAABB'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor on data.

		:param scale: The scale factor."""
		self.center *= scale
		self.radius *= scale
		if hasattr(self, "div2_aabb"):
			for vector in self.div2_aabb.corners:
				vector.x *= scale
				vector.y *= scale
				vector.z *= scale


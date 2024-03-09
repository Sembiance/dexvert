from nifgen.utils.mathutils import matTransposed, matvecMul, vecAdd, matMul
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkConvexShapeBase import BhkConvexShapeBase
from nifgen.formats.nif.imports import name_type_map


class BhkConvexTransformShape(BhkConvexShapeBase):

	"""
	Contains a bhkConvexShape and an additional transform for that shape.
	The advantage of using bhkConvexTransformShape over bhkTransformShape is that it does not require additional agents to be created as it is itself convex.
	"""

	__name__ = 'bhkConvexTransformShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The shape that this object transforms.
		self.shape = name_type_map['Ref'](self.context, 0, name_type_map['BhkConvexShape'])

		# The material of the shape.
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		self.radius = name_type_map['Float'](self.context, 0, None)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])

		# A transform matrix.
		self.transform = name_type_map['Matrix44'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shape', name_type_map['Ref'], (0, name_type_map['BhkConvexShape']), (False, None), (None, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)
		yield 'transform', name_type_map['Matrix44'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shape', name_type_map['Ref'], (0, name_type_map['BhkConvexShape']), (False, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, None)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		yield 'transform', name_type_map['Matrix44'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor <scale> on data."""
		super().apply_scale(scale)
		# apply scale on translation
		self.transform.m_14 *= scale
		self.transform.m_24 *= scale
		self.transform.m_34 *= scale

	def get_mass_center_inertia(self, density=1, solid=True):
		"""Return mass, center, and inertia tensor."""
		# get shape mass, center, and inertia
		mass, center, inertia = self.get_shape_mass_center_inertia(
			density=density, solid=solid)
		# get transform matrix and translation vector
		transform = self.transform.get_matrix_33().as_tuple()
		transform_transposed = matTransposed(transform)
		translation = ( self.transform.m_14, self.transform.m_24, self.transform.m_34 )
		# transform center and inertia
		center = matvecMul(transform, center)
		center = vecAdd(center, translation)
		inertia = matMul(matMul(transform_transposed, inertia), transform)
		# return updated mass center and inertia
		return mass, center, inertia



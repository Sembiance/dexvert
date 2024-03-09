from nifgen.utils.mathutils import vecAdd, vecscalarMul, matAdd
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkShapeCollection import BhkShapeCollection
from nifgen.formats.nif.imports import name_type_map


class BhkListShape(BhkShapeCollection):

	"""
	A list of shapes.
	
	Shapes collected in a bhkListShape may not have the correct collision sound/FX due to HavokMaterial issues.
	Do not put a bhkPackedNiTriStripsShape in the Sub Shapes. Use a separate collision nodes without a list shape for those.
	"""

	__name__ = 'bhkListShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.num_sub_shapes = name_type_map['Uint'].from_value(1)

		# List of shapes. Max of 256.
		self.sub_shapes = Array(self.context, 0, name_type_map['BhkShape'], (0,), name_type_map['Ref'])

		# The material of the shape.
		self.material = name_type_map['HavokMaterial'](self.context, 0, None)
		self.child_shape_property = name_type_map['BhkWorldObjCInfoProperty'](self.context, 0, None)
		self.child_filter_property = name_type_map['BhkWorldObjCInfoProperty'](self.context, 0, None)
		self.num_filters = name_type_map['Uint'](self.context, 0, None)

		# Always zeroed. Seemingly unused, or 0 for all values means no override.
		self.filters = Array(self.context, 0, None, (0,), name_type_map['HavokFilter'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'num_sub_shapes', name_type_map['Uint'], (0, None), (False, 1), (None, None)
		yield 'sub_shapes', Array, (0, name_type_map['BhkShape'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None), (None, None)
		yield 'child_shape_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None), (None, None)
		yield 'child_filter_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None), (None, None)
		yield 'num_filters', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'filters', Array, (0, None, (None,), name_type_map['HavokFilter']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'num_sub_shapes', name_type_map['Uint'], (0, None), (False, 1)
		yield 'sub_shapes', Array, (0, name_type_map['BhkShape'], (instance.num_sub_shapes,), name_type_map['Ref']), (False, None)
		yield 'material', name_type_map['HavokMaterial'], (0, None), (False, None)
		yield 'child_shape_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None)
		yield 'child_filter_property', name_type_map['BhkWorldObjCInfoProperty'], (0, None), (False, None)
		yield 'num_filters', name_type_map['Uint'], (0, None), (False, None)
		yield 'filters', Array, (0, None, (instance.num_filters,), name_type_map['HavokFilter']), (False, None)

	def get_mass_center_inertia(self, density = 1, solid = True):
		"""Return center of gravity and area."""
		subshapes_mci = [ subshape.get_mass_center_inertia(density = density,
														solid = solid)
						  for subshape in self.sub_shapes ]
		total_mass = 0
		total_center = (0, 0, 0)
		total_inertia = ((0, 0, 0), (0, 0, 0), (0, 0, 0))

		# get total mass
		for mass, center, inertia in subshapes_mci:
			total_mass += mass
		if total_mass == 0:
			return 0, (0, 0, 0), ((0, 0, 0), (0, 0, 0), (0, 0, 0))

		# get average center and inertia
		for mass, center, inertia in subshapes_mci:
			total_center = vecAdd(total_center,
								  vecscalarMul(center, mass / total_mass))
			total_inertia = matAdd(total_inertia, inertia)
		return total_mass, total_center, total_inertia

	def add_shape(self, shape, front = False):
		"""Add shape to list."""
		# check if it's already there
		if shape in self.sub_shapes: return
		# increase number of shapes
		num_shapes = self.num_sub_shapes
		self.num_sub_shapes = num_shapes + 1
		# add the shape
		if not front:
			self.sub_shapes.append(shape)
		else:
			self.sub_shapes[:] = [shape, *self.sub_shapes]
		# expand list of unknown ints as well
		self.num_unknown_ints = num_shapes + 1
		self.unknown_ints.append(0)

	def remove_shape(self, shape):
		"""Remove a shape from the shape list."""
		# get list of shapes excluding the shape to remove
		shapes = [s for s in self.sub_shapes if s != shape]
		# set sub_shapes to this list
		self.num_sub_shapes = len(shapes)
		self.sub_shapes[:] = shapes
		# update unknown ints
		self.num_unknown_ints = len(shapes)
		self.unknown_ints[:] = (0, ) * len(shapes)


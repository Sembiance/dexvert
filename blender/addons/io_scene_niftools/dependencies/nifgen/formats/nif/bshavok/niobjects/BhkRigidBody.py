from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkEntity import BhkEntity
from nifgen.formats.nif.imports import name_type_map


class BhkRigidBody(BhkEntity):

	"""
	This is the default body type for all "normal" usable and static world objects. The "T" suffix
	marks this body as active for translation and rotation, a normal bhkRigidBody ignores those
	properties. Because the properties are equal, a bhkRigidBody may be renamed into a bhkRigidBodyT and vice-versa.
	"""

	__name__ = 'bhkRigidBody'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.rigid_body_info = name_type_map['BhkRigidBodyCInfo2014'](self.context, 0, None)
		self.num_constraints = name_type_map['Uint'](self.context, 0, None)
		self.constraints = Array(self.context, 0, name_type_map['BhkSerializable'], (0,), name_type_map['Ref'])

		# 1 = respond to wind
		self.body_flags = name_type_map['Ushort'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'rigid_body_info', name_type_map['BhkRigidBodyCInfo550660'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'rigid_body_info', name_type_map['BhkRigidBodyCInfo2010'], (0, None), (False, None), (lambda context: (context.bs_header.bs_version >= 83) and (not (context.bs_header.bs_version == 130)), None)
		yield 'rigid_body_info', name_type_map['BhkRigidBodyCInfo2014'], (0, None), (False, None), (lambda context: context.bs_header.bs_version == 130, None)
		yield 'num_constraints', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'constraints', Array, (0, name_type_map['BhkSerializable'], (None,), name_type_map['Ref']), (False, None), (None, None)
		yield 'body_flags', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version < 76, None)
		yield 'body_flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.bs_header.bs_version >= 76, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version <= 34:
			yield 'rigid_body_info', name_type_map['BhkRigidBodyCInfo550660'], (0, None), (False, None)
		if (instance.context.bs_header.bs_version >= 83) and (not (instance.context.bs_header.bs_version == 130)):
			yield 'rigid_body_info', name_type_map['BhkRigidBodyCInfo2010'], (0, None), (False, None)
		if instance.context.bs_header.bs_version == 130:
			yield 'rigid_body_info', name_type_map['BhkRigidBodyCInfo2014'], (0, None), (False, None)
		yield 'num_constraints', name_type_map['Uint'], (0, None), (False, None)
		yield 'constraints', Array, (0, name_type_map['BhkSerializable'], (instance.num_constraints,), name_type_map['Ref']), (False, None)
		if instance.context.bs_header.bs_version < 76:
			yield 'body_flags', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.bs_header.bs_version >= 76:
			yield 'body_flags', name_type_map['Ushort'], (0, None), (False, None)

	def apply_scale(self, scale):
		"""Apply scale factor <scale> on data."""
		super().apply_scale(scale)
		# apply scale on transform
		self.rigid_body_info.translation.x *= scale
		self.rigid_body_info.translation.y *= scale
		self.rigid_body_info.translation.z *= scale

		# apply scale on center of gravity
		self.rigid_body_info.center.x *= scale
		self.rigid_body_info.center.y *= scale
		self.rigid_body_info.center.z *= scale

		# apply scale on inertia tensor
		self.rigid_body_info.inertia_tensor.m_11 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_12 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_13 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_14 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_21 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_22 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_23 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_24 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_31 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_32 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_33 *= (scale ** 2)
		self.rigid_body_info.inertia_tensor.m_34 *= (scale ** 2)

	def update_mass_center_inertia(self, density=1, solid=True, mass=None):
		"""Look at all the objects under this rigid body and update the mass,
		center of gravity, and inertia tensor accordingly. If the C{mass} parameter
		is given then the C{density} argument is ignored."""
		if not mass is None:
			density = 1

		calc_mass, center, inertia = self.get_shape_mass_center_inertia(
			density=density, solid=solid)

		self.mass = calc_mass
		self.center.x, self.center.y, self.center.z = center
		self.rigid_body_info.inertia_tensor.m_11 = inertia[0][0]
		self.rigid_body_info.inertia_tensor.m_12 = inertia[0][1]
		self.rigid_body_info.inertia_tensor.m_13 = inertia[0][2]
		self.rigid_body_info.inertia_tensor.m_14 = 0
		self.rigid_body_info.inertia_tensor.m_21 = inertia[1][0]
		self.rigid_body_info.inertia_tensor.m_22 = inertia[1][1]
		self.rigid_body_info.inertia_tensor.m_23 = inertia[1][2]
		self.rigid_body_info.inertia_tensor.m_24 = 0
		self.rigid_body_info.inertia_tensor.m_31 = inertia[2][0]
		self.rigid_body_info.inertia_tensor.m_32 = inertia[2][1]
		self.rigid_body_info.inertia_tensor.m_33 = inertia[2][2]
		self.rigid_body_info.inertia_tensor.m_34 = 0

		if not mass is None:
			mass_correction = mass / calc_mass if calc_mass != 0 else 1
			self.mass = mass
			self.rigid_body_info.inertia_tensor.m_11 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_12 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_13 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_14 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_21 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_22 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_23 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_24 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_31 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_32 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_33 *= mass_correction
			self.rigid_body_info.inertia_tensor.m_34 *= mass_correction



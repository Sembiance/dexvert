import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif import versions
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObjectNET import NiObjectNET


class NiAVObject(NiObjectNET):

	"""
	Abstract audio-visual base class from which all of Gamebryo's scene graph objects inherit.
	"""

	__name__ = 'NiAVObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Basic flags for AV objects. For Bethesda streams above 26 only.
		# ALL: FO4 lacks the 0x80000 flag always. Skyrim lacks it sometimes.
		# BSTreeNode: 0x8080E (pre-FO4), 0x400E (FO4)
		# BSLeafAnimNode: 0x808000E (pre-FO4), 0x500E (FO4)
		# BSDamageStage, BSBlastNode: 0x8000F (pre-FO4), 0x2000000F (FO4)

		# Basic flags for AV objects.
		self.flags = name_type_map['Ushort'](self.context, 0, None)

		# The translation vector.
		self.translation = name_type_map['Vector3'](self.context, 0, None)

		# The rotation part of the transformation matrix.
		self.rotation = name_type_map['Matrix33'](self.context, 0, None)

		# Scaling part (only uniform scaling is supported).
		self.scale = name_type_map['Float'].from_value(1.0)

		# Unknown function. Always seems to be (0, 0, 0)
		self.velocity = name_type_map['Vector3'](self.context, 0, None)
		self.num_properties = name_type_map['Uint'](self.context, 0, None)

		# All rendering properties attached to this object.
		self.properties = Array(self.context, 0, name_type_map['NiProperty'], (0,), name_type_map['Ref'])
		self.unknown_1 = Array(self.context, 0, None, (0,), name_type_map['Uint'])
		self.unknown_2 = name_type_map['Byte'](self.context, 0, None)
		self.has_bounding_volume = name_type_map['Bool'](self.context, 0, None)
		self.bounding_volume = name_type_map['BoundingVolume'](self.context, 0, None)
		self.collision_object = name_type_map['Ref'](self.context, 0, name_type_map['NiCollisionObject'])

		# Could be one byte and a uint. Always 00 17 00 00 00?
		self.unknown_q_q_speed_ni_a_v_object_bytes = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['Uint'], (0, None), (False, 524302), (lambda context: context.bs_header.bs_version > 26, None)
		yield 'flags', name_type_map['Ushort'], (0, None), (False, None), (lambda context: context.version >= 50331648 and context.bs_header.bs_version <= 26, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None), (None, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'velocity', name_type_map['Vector3'], (0, None), (False, None), (lambda context: context.version <= 67240448, None)
		yield 'num_properties', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'properties', Array, (0, name_type_map['NiProperty'], (None,), name_type_map['Ref']), (False, None), (lambda context: context.bs_header.bs_version <= 34, None)
		yield 'unknown_1', Array, (0, None, (4,), name_type_map['Uint']), (False, None), (lambda context: context.version <= 33751040, None)
		yield 'unknown_2', name_type_map['Byte'], (0, None), (False, None), (lambda context: context.version <= 33751040, None)
		yield 'has_bounding_volume', name_type_map['Bool'], (0, None), (False, None), (lambda context: 50331648 <= context.version <= 67240448, None)
		yield 'bounding_volume', name_type_map['BoundingVolume'], (0, None), (False, None), (lambda context: 50331648 <= context.version <= 67240448, True)
		yield 'collision_object', name_type_map['Ref'], (0, name_type_map['NiCollisionObject']), (False, None), (lambda context: context.version >= 167772416, None)
		yield 'unknown_q_q_speed_ni_a_v_object_bytes', Array, (0, None, (5,), name_type_map['Byte']), (False, None), (lambda context: 335676695 <= context.version <= 335676695, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if instance.context.bs_header.bs_version > 26:
			if (versions.is_v20_2_0_7_sky(instance.context)) and isinstance(instance, name_type_map['BSLODTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 134742030)
			elif (versions.is_v20_2_0_7_sse(instance.context)) and isinstance(instance, name_type_map['BSLODTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 134217742)
			elif (versions.is_v20_2_0_7_fo3(instance.context)) and isinstance(instance, name_type_map['BSOrderedNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif (versions.is_v20_2_0_7_fo4(instance.context)) and isinstance(instance, name_type_map['BSOrderedNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 8206)
			elif isinstance(instance, name_type_map['BSOrderedNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 532494)
			elif (versions.is_v20_2_0_7_fo4(instance.context)) and isinstance(instance, name_type_map['BSDamageStage']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 536870927)
			elif isinstance(instance, name_type_map['BSDamageStage']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524303)
			elif (versions.is_v20_2_0_7_fo4(instance.context)) and isinstance(instance, name_type_map['BSBlastNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 536870927)
			elif isinstance(instance, name_type_map['BSBlastNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524303)
			elif isinstance(instance, name_type_map['BSDebrisNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524303)
			elif (versions.is_v20_2_0_7_fo4(instance.context)) and isinstance(instance, name_type_map['BSTreeNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 16398)
			elif isinstance(instance, name_type_map['BSTreeNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 526350)
			elif (versions.is_v20_2_0_7_fo4(instance.context)) and isinstance(instance, name_type_map['BSLeafAnimNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 20494)
			elif isinstance(instance, name_type_map['BSLeafAnimNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 134742030)
			elif (versions.is_v20_2_0_7_fo3(instance.context)) and isinstance(instance, name_type_map['BSSegmentedTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['BSSegmentedTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			elif isinstance(instance, name_type_map['NiTriStrips']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['NiTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['BSStripParticleSystem']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif (versions.is_v20_2_0_7_fo4(instance.context)) and isinstance(instance, name_type_map['BSMasterParticleSystem']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			elif (versions.is_v20_2_0_7_fo4(instance.context)) and isinstance(instance, name_type_map['NiParticleSystem']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			elif isinstance(instance, name_type_map['BSMasterParticleSystem']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['NiParticleSystem']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['BSFadeNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['BSMeshLODTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 4110)
			elif isinstance(instance, name_type_map['BSSubIndexTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			elif (versions.is_v20_2_0_7_sse(instance.context)) and isinstance(instance, name_type_map['BSTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['BSTriShape']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			elif (versions.is_v20_2_0_7_fo3(instance.context)) and isinstance(instance, name_type_map['BSMultiBoundNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 526350)
			elif isinstance(instance, name_type_map['BSMultiBoundNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			elif (versions.is_v20_2_0_7_fo3(instance.context)) and isinstance(instance, name_type_map['NiLight']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['NiLight']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			elif (versions.is_v20_2_0_7_fo3(instance.context)) and isinstance(instance, name_type_map['NiNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
			elif isinstance(instance, name_type_map['NiNode']):
				yield 'flags', name_type_map['Uint'], (0, None), (False, 14)
			else:
				yield 'flags', name_type_map['Uint'], (0, None), (False, 524302)
		if instance.context.version >= 50331648 and instance.context.bs_header.bs_version <= 26:
			yield 'flags', name_type_map['Ushort'], (0, None), (False, None)
		yield 'translation', name_type_map['Vector3'], (0, None), (False, None)
		yield 'rotation', name_type_map['Matrix33'], (0, None), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.version <= 67240448:
			yield 'velocity', name_type_map['Vector3'], (0, None), (False, None)
		if instance.context.bs_header.bs_version <= 34:
			yield 'num_properties', name_type_map['Uint'], (0, None), (False, None)
			yield 'properties', Array, (0, name_type_map['NiProperty'], (instance.num_properties,), name_type_map['Ref']), (False, None)
		if instance.context.version <= 33751040:
			yield 'unknown_1', Array, (0, None, (4,), name_type_map['Uint']), (False, None)
			yield 'unknown_2', name_type_map['Byte'], (0, None), (False, None)
		if 50331648 <= instance.context.version <= 67240448:
			yield 'has_bounding_volume', name_type_map['Bool'], (0, None), (False, None)
		if 50331648 <= instance.context.version <= 67240448 and instance.has_bounding_volume:
			yield 'bounding_volume', name_type_map['BoundingVolume'], (0, None), (False, None)
		if instance.context.version >= 167772416:
			yield 'collision_object', name_type_map['Ref'], (0, name_type_map['NiCollisionObject']), (False, None)
		if 335676695 <= instance.context.version <= 335676695:
			yield 'unknown_q_q_speed_ni_a_v_object_bytes', Array, (0, None, (5,), name_type_map['Byte']), (False, None)

	"""
	>>> from pyffi.formats.nif import NifFormat
	>>> node = NifFormat.NiNode()
	>>> prop1 = NifFormat.NiProperty()
	>>> prop1.name = "hello"
	>>> prop2 = NifFormat.NiProperty()
	>>> prop2.name = "world"
	>>> node.get_properties()
	[]
	>>> node.set_properties([prop1, prop2])
	>>> [prop.name for prop in node.get_properties()]
	[b'hello', b'world']
	>>> [prop.name for prop in node.properties]
	[b'hello', b'world']
	>>> node.set_properties([])
	>>> node.get_properties()
	[]
	>>> # now set them the other way around
	>>> node.set_properties([prop2, prop1])
	>>> [prop.name for prop in node.get_properties()]
	[b'world', b'hello']
	>>> [prop.name for prop in node.properties]
	[b'world', b'hello']
	>>> node.remove_property(prop2)
	>>> [prop.name for prop in node.properties]
	[b'hello']
	>>> node.add_property(prop2)
	>>> [prop.name for prop in node.properties]
	[b'hello', b'world']
	"""
	def add_property(self, prop):
		"""Add the given property to the property list.

		:param prop: The property block to add.
		:type prop: L{NifFormat.NiProperty}
		"""
		num_props = self.num_properties
		self.num_properties = num_props + 1
		self.properties.append(prop)

	def remove_property(self, prop):
		"""Remove the given property to the property list.

		:param prop: The property block to remove.
		:type prop: L{NifFormat.NiProperty}
		"""
		self.set_properties([otherprop for otherprop in self.get_properties()
							if not(otherprop is prop)])

	def get_properties(self):
		"""Return a list of the properties of the block.

		:return: The list of properties.
		:rtype: ``list`` of L{NifFormat.NiProperty}
		"""
		return [prop for prop in self.properties]

	def set_properties(self, proplist):
		"""Set the list of properties from the given list (destroys existing list).

		:param proplist: The list of property blocks to set.
		:type proplist: ``list`` of L{NifFormat.NiProperty}
		"""
		self.num_properties = len(proplist)
		self.reset_field("properties")
		for i, prop in enumerate(proplist):
			self.properties[i] = prop

	def get_transform(self, relative_to=None):
		"""Return scale, rotation, and translation into a single 4x4
		matrix, relative to the C{relative_to} block (which should be
		another NiAVObject connecting to this block). If C{relative_to} is
		``None``, then returns the transform stored in C{self}, or
		equivalently, the target is assumed to be the parent.

		:param relative_to: The block relative to which the transform must
			be calculated. If ``None``, the local transform is returned.
		"""
		m = NifFormat.classes.Matrix44()
		m.set_scale_rotation_translation(self.scale, self.rotation, self.translation)
		if not relative_to: return m
		# find chain from relative_to to self
		chain = relative_to.find_chain(self, block_type = NifFormat.classes.NiAVObject)
		if not chain:
			raise ValueError(
				'cannot find a chain of NiAVObject blocks '
				'between %s and %s.' % (self.name, relative_to.name))
		# and multiply with all transform matrices (not including relative_to)
		for block in reversed(chain[1:-1]):
			m *= block.get_transform()
		return m

	def set_transform(self, m):
		"""Set rotation, translation, and scale, from a 4x4 matrix.

		:param m: The matrix to which the transform should be set."""
		scale, rotation, translation = m.get_scale_rotation_translation()

		self.scale = scale

		self.rotation.m_11 = rotation.m_11
		self.rotation.m_12 = rotation.m_12
		self.rotation.m_13 = rotation.m_13
		self.rotation.m_21 = rotation.m_21
		self.rotation.m_22 = rotation.m_22
		self.rotation.m_23 = rotation.m_23
		self.rotation.m_31 = rotation.m_31
		self.rotation.m_32 = rotation.m_32
		self.rotation.m_33 = rotation.m_33

		self.translation.x = translation.x
		self.translation.y = translation.y
		self.translation.z = translation.z

	def apply_scale(self, scale):
		"""Apply scale factor on data.

		:param scale: The scale factor."""
		super().apply_scale(scale)
		# apply scale on translation
		self.translation.x *= scale
		self.translation.y *= scale
		self.translation.z *= scale
		# apply scale on bounding volume
		self.bounding_volume.apply_scale(scale)


from nifgen.formats.nif import versions
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiObject import NiObject


class NiPSysModifier(NiObject):

	"""
	Abstract base class for all particle system modifiers.
	"""

	__name__ = 'NiPSysModifier'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Used to locate the modifier.
		self.name = name_type_map['String'](self.context, 0, None)

		# Modifier's priority in the particle modifier chain.
		self.order = name_type_map['NiPSysModifierOrder'].ORDER_GENERAL

		# NiParticleSystem parent of this modifier.
		self.target = name_type_map['Ptr'](self.context, 0, name_type_map['NiParticleSystem'])

		# Whether or not the modifier is active.
		self.active = name_type_map['Bool'].from_value(True)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'name', name_type_map['String'], (0, None), (False, None), (None, None)
		yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL), (None, None)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiParticleSystem']), (False, None), (None, None)
		yield 'active', name_type_map['Bool'], (0, None), (False, True), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'name', name_type_map['String'], (0, None), (False, None)
		if isinstance(instance, name_type_map['NiPSysPartSpawnModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_WORLDSHIFT_PARTSPAWN)
		elif (versions.is_v20_2_0_7_sky(instance.context) or versions.is_v20_2_0_7_sse(instance.context)) and isinstance(instance, name_type_map['BSPSysStripUpdateModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_SK_BSSTRIPUPDATE)
		elif (versions.is_v20_2_0_7_fo3(instance.context)) and isinstance(instance, name_type_map['BSPSysStripUpdateModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_FO3_BSSTRIPUPDATE)
		elif isinstance(instance, name_type_map['BSPSysLODModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_BSLOD)
		elif isinstance(instance, name_type_map['BSPSysRecycleBoundModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_POSTPOS_UPDATE)
		elif isinstance(instance, name_type_map['BSWindModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_FORCE)
		elif isinstance(instance, name_type_map['BSParentVelocityModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		elif isinstance(instance, name_type_map['BSPSysSubTexModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		elif isinstance(instance, name_type_map['BSPSysSimpleColorModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		elif isinstance(instance, name_type_map['BSPSysScaleModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		elif isinstance(instance, name_type_map['BSPSysInheritVelocityModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_EMITTER)
		elif isinstance(instance, name_type_map['NiPSysBoundUpdateModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_BOUND_UPDATE)
		elif isinstance(instance, name_type_map['NiPSysMeshUpdateModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_POSTPOS_UPDATE)
		elif isinstance(instance, name_type_map['NiPSysPositionModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_POS_UPDATE)
		elif isinstance(instance, name_type_map['NiPSysColliderManager']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_COLLIDER)
		elif isinstance(instance, name_type_map['NiPSysGravityModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_FORCE)
		elif isinstance(instance, name_type_map['NiPSysFieldModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_FORCE)
		elif isinstance(instance, name_type_map['NiPSysDragModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_FORCE)
		elif isinstance(instance, name_type_map['NiPSysBombModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_FORCE)
		elif isinstance(instance, name_type_map['NiPSysRotationModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		elif isinstance(instance, name_type_map['NiPSysGrowFadeModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		elif isinstance(instance, name_type_map['NiPSysColorModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		elif isinstance(instance, name_type_map['NiPSysSpawnModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_EMITTER)
		elif isinstance(instance, name_type_map['NiPSysVolumeEmitter']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_EMITTER)
		elif isinstance(instance, name_type_map['NiPSysMeshEmitter']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_EMITTER)
		elif isinstance(instance, name_type_map['NiPSysAgeDeathModifier']):
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_KILLOLDPARTICLES)
		else:
			yield 'order', name_type_map['NiPSysModifierOrder'], (0, None), (False, name_type_map['NiPSysModifierOrder'].ORDER_GENERAL)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiParticleSystem']), (False, None)
		yield 'active', name_type_map['Bool'], (0, None), (False, True)

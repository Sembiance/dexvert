from nifgen.formats.nif import versions
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiCollisionObject import NiCollisionObject


class BhkNiCollisionObject(NiCollisionObject):

	"""
	Abstract base class to merge NiCollisionObject with Bethesda Havok.
	"""

	__name__ = 'bhkNiCollisionObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# OB-FO3: Add 0x28 (SET_LOCAL | USE_VEL) for ANIM_STATIC layer objects.
		# Post-FO3: Always add 0x80 (SYNC_ON_UPDATE).
		self.flags = name_type_map['BhkCOFlags'].from_value(1)
		self.body = name_type_map['Ref'](self.context, 0, name_type_map['BhkWorldObject'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 1), (None, None)
		yield 'body', name_type_map['Ref'], (0, name_type_map['BhkWorldObject']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		if (versions.is_v20_2_0_7_fo3(instance.context) or versions.is_v20_0_0_5_obl(instance.context)) and isinstance(instance, name_type_map['BhkBlendCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 9)
		elif isinstance(instance, name_type_map['BhkBlendCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 137)
		elif (versions.is_v20_2_0_7_fo3(instance.context) or versions.is_v20_0_0_5_obl(instance.context)) and isinstance(instance, name_type_map['BhkSPCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 1)
		elif isinstance(instance, name_type_map['BhkSPCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 129)
		elif (versions.is_v20_2_0_7_fo3(instance.context) or versions.is_v20_0_0_5_obl(instance.context)) and isinstance(instance, name_type_map['BhkPCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 1)
		elif isinstance(instance, name_type_map['BhkPCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 129)
		elif (versions.is_v20_2_0_7_fo3(instance.context) or versions.is_v20_0_0_5_obl(instance.context)) and isinstance(instance, name_type_map['BhkCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 1)
		elif isinstance(instance, name_type_map['BhkCollisionObject']):
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 129)
		else:
			yield 'flags', name_type_map['BhkCOFlags'], (0, None), (False, 1)
		yield 'body', name_type_map['Ref'], (0, name_type_map['BhkWorldObject']), (False, None)

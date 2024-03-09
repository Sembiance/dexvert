from nifgen.formats.nif.bshavok.niobjects.BhkSerializable import BhkSerializable
from nifgen.formats.nif.imports import name_type_map


class BhkWorldObject(BhkSerializable):

	"""
	Bethesda extension of hkpWorldObject, the base class for hkpEntity and hkpPhantom.
	"""

	__name__ = 'bhkWorldObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# The shape for this collision object.
		self.shape = name_type_map['Ref'](self.context, 0, name_type_map['BhkShape'])
		self.unknown_int = name_type_map['Uint'](self.context, 0, None)
		self.havok_filter = name_type_map['HavokFilter'](self.context, 0, None)
		self.world_object_info = name_type_map['BhkWorldObjectCInfo'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'shape', name_type_map['Ref'], (0, name_type_map['BhkShape']), (False, None), (None, None)
		yield 'unknown_int', name_type_map['Uint'], (0, None), (False, None), (lambda context: context.version <= 167772418, None)
		yield 'havok_filter', name_type_map['HavokFilter'], (0, None), (False, None), (None, None)
		yield 'world_object_info', name_type_map['BhkWorldObjectCInfo'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'shape', name_type_map['Ref'], (0, name_type_map['BhkShape']), (False, None)
		if instance.context.version <= 167772418:
			yield 'unknown_int', name_type_map['Uint'], (0, None), (False, None)
		yield 'havok_filter', name_type_map['HavokFilter'], (0, None), (False, None)
		yield 'world_object_info', name_type_map['BhkWorldObjectCInfo'], (0, None), (False, None)

from nifgen.formats.nif.bshavok.niobjects.BhkCollisionObject import BhkCollisionObject
from nifgen.formats.nif.imports import name_type_map


class BhkBlendCollisionObject(BhkCollisionObject):

	"""
	Bethesda Havok object used in skeletons.
	"""

	__name__ = 'bhkBlendCollisionObject'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.heir_gain = name_type_map['Float'].from_value(1.0)
		self.vel_gain = name_type_map['Float'].from_value(1.0)
		self.unknown_float_1 = name_type_map['Float'](self.context, 0, None)
		self.unknown_float_2 = name_type_map['Float'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'heir_gain', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'vel_gain', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None), (lambda context: context.bs_header.bs_version < 9, None)
		yield 'unknown_float_2', name_type_map['Float'], (0, None), (False, None), (lambda context: context.bs_header.bs_version < 9, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'heir_gain', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'vel_gain', name_type_map['Float'], (0, None), (False, 1.0)
		if instance.context.bs_header.bs_version < 9:
			yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None)
			yield 'unknown_float_2', name_type_map['Float'], (0, None), (False, None)

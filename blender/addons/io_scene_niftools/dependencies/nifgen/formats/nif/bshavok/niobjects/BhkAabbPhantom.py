from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkPhantom import BhkPhantom
from nifgen.formats.nif.imports import name_type_map


class BhkAabbPhantom(BhkPhantom):

	"""
	Bethesda extension of hkpAabbPhantom. A non-physical object made up of only an AABB.
	- Very fast as they use only broadphase collision detection.
	- Used for triggers/regions where a shape is not necessary.
	"""

	__name__ = 'bhkAabbPhantom'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.aabb = name_type_map['HkAabb'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)
		yield 'aabb', name_type_map['HkAabb'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		yield 'aabb', name_type_map['HkAabb'], (0, None), (False, None)

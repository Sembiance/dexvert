from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkShapePhantom import BhkShapePhantom
from nifgen.formats.nif.imports import name_type_map


class BhkSimpleShapePhantom(BhkShapePhantom):

	"""
	Bethesda extension of hkpSimpleShapePhantom. A Phantom with arbitrary shape and transform.
	Does not do any narrowphase caching, in contrast to hkpCachingShapePhantom.
	"""

	__name__ = 'bhkSimpleShapePhantom'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.unused_01 = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		self.transform = name_type_map['Matrix44'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None), (None, None)
		yield 'transform', name_type_map['Matrix44'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (8,), name_type_map['Byte']), (False, None)
		yield 'transform', name_type_map['Matrix44'], (0, None), (False, None)

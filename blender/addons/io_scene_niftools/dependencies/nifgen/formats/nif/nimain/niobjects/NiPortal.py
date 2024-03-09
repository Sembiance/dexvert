from nifgen.array import Array
from nifgen.formats.nif.imports import name_type_map
from nifgen.formats.nif.nimain.niobjects.NiAVObject import NiAVObject


class NiPortal(NiAVObject):

	"""
	NiPortal objects are grouping nodes that support aggressive visibility culling.
	They represent flat polygonal regions through which a part of a scene graph can be viewed.
	"""

	__name__ = 'NiPortal'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		self.portal_flags = name_type_map['Ushort'](self.context, 0, None)

		# Unused in 20.x, possibly also 10.x.
		self.plane_count = name_type_map['Ushort'](self.context, 0, None)
		self.num_vertices = name_type_map['Ushort'](self.context, 0, None)
		self.vertices = Array(self.context, 0, None, (0,), name_type_map['Vector3'])

		# Root of the scenegraph which is to be seen through this portal.
		self.adjoiner = name_type_map['Ptr'](self.context, 0, name_type_map['NiNode'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'portal_flags', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'plane_count', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None), (None, None)
		yield 'vertices', Array, (0, None, (None,), name_type_map['Vector3']), (False, None), (None, None)
		yield 'adjoiner', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'portal_flags', name_type_map['Ushort'], (0, None), (False, None)
		yield 'plane_count', name_type_map['Ushort'], (0, None), (False, None)
		yield 'num_vertices', name_type_map['Ushort'], (0, None), (False, None)
		yield 'vertices', Array, (0, None, (instance.num_vertices,), name_type_map['Vector3']), (False, None)
		yield 'adjoiner', name_type_map['Ptr'], (0, name_type_map['NiNode']), (False, None)

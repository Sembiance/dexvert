from nifgen.formats.nif.bshavok.niobjects.BhkShape import BhkShape
from nifgen.formats.nif.imports import name_type_map


class BhkCompressedMeshShape(BhkShape):

	"""
	Compressed collision mesh.
	"""

	__name__ = 'bhkCompressedMeshShape'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Points to root node?
		self.target = name_type_map['Ptr'](self.context, 0, name_type_map['NiAVObject'])
		self.user_data = name_type_map['Uint'](self.context, 0, None)

		# A shell that is added around the shape.
		self.radius = name_type_map['Float'].from_value(0.005)
		self.unknown_float_1 = name_type_map['Float'](self.context, 0, None)

		# Scale
		self.scale = name_type_map['Vector4'].from_value((1.0, 1.0, 1.0, 0.0))

		# A shell that is added around the shape.
		self.radius_copy = name_type_map['Float'].from_value(0.005)

		# Scale
		self.scale_copy = name_type_map['Vector4'].from_value((1.0, 1.0, 1.0, 0.0))

		# The collision mesh data.
		self.data = name_type_map['Ref'](self.context, 0, name_type_map['BhkCompressedMeshShapeData'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None), (None, None)
		yield 'user_data', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.005), (None, None)
		yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'scale', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0)), (None, None)
		yield 'radius_copy', name_type_map['Float'], (0, None), (False, 0.005), (None, None)
		yield 'scale_copy', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0)), (None, None)
		yield 'data', name_type_map['Ref'], (0, name_type_map['BhkCompressedMeshShapeData']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'target', name_type_map['Ptr'], (0, name_type_map['NiAVObject']), (False, None)
		yield 'user_data', name_type_map['Uint'], (0, None), (False, None)
		yield 'radius', name_type_map['Float'], (0, None), (False, 0.005)
		yield 'unknown_float_1', name_type_map['Float'], (0, None), (False, None)
		yield 'scale', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0))
		yield 'radius_copy', name_type_map['Float'], (0, None), (False, 0.005)
		yield 'scale_copy', name_type_map['Vector4'], (0, None), (False, (1.0, 1.0, 1.0, 0.0))
		yield 'data', name_type_map['Ref'], (0, name_type_map['BhkCompressedMeshShapeData']), (False, None)

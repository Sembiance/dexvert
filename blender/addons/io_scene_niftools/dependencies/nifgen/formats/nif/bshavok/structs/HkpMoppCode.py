from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.nif.imports import name_type_map


class HkpMoppCode(BaseStruct):

	__name__ = 'hkpMoppCode'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# Number of bytes for MOPP data.
		self.data_size = name_type_map['Uint'](self.context, 0, None)

		# XYZ: Origin of the object in mopp coordinates. This is the minimum of all vertices in the packed shape along each axis, minus the radius of the child bhkPackedNiTriStripsShape/
		# bhkCompressedMeshShape.
		# W: The scaling factor to quantize the MOPP: the quantization factor is equal to 256*256 divided by this number.
		# In Oblivion and Skyrim files, scale is taken equal to 256*256*254 / (size + 2 * radius) where size is the largest dimension of the bounding box of the packed shape,
		# and radius is the radius of the child bhkPackedNiTriStripsShape/bhkCompressedMeshShape.
		self.offset = name_type_map['Vector4'](self.context, 0, None)

		# Tells if MOPP Data was organized into smaller chunks (PS3) or not (PC)
		self.build_type = name_type_map['HkMoppCodeBuildType'](self.context, 0, None)

		# The tree of bounding volume data.
		self.data = Array(self.context, 0, None, (0,), name_type_map['Byte'])
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'data_size', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'offset', name_type_map['Vector4'], (0, None), (False, None), (lambda context: context.version >= 167837696, None)
		yield 'build_type', name_type_map['HkMoppCodeBuildType'], (0, None), (False, None), (lambda context: context.bs_header.bs_version > 34, None)
		yield 'data', Array, (0, None, (None,), name_type_map['Byte']), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'data_size', name_type_map['Uint'], (0, None), (False, None)
		if instance.context.version >= 167837696:
			yield 'offset', name_type_map['Vector4'], (0, None), (False, None)
		if instance.context.bs_header.bs_version > 34:
			yield 'build_type', name_type_map['HkMoppCodeBuildType'], (0, None), (False, None)
		yield 'data', Array, (0, None, (instance.data_size,), name_type_map['Byte']), (False, None)

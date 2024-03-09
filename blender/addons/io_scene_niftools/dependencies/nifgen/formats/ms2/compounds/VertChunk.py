from nifgen.base_struct import BaseStruct
from nifgen.formats.ms2.imports import name_type_map


class VertChunk(BaseStruct):

	"""
	JWE2 Biosyn: 16 bytes
	"""

	__name__ = 'VertChunk'


	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)

		# apparently also used for scaling the mesh: pack_base / 512 / 2048 = scale
		self.scale = name_type_map['Float'](self.context, 0, None)

		# the usual mesh scale: pack_base / 512, also added as offset during vertex packing
		self.pack_base = name_type_map['Float'](self.context, 0, None)

		# byte offset from start of vert buffer in bytes
		self.vertex_offset = name_type_map['Uint'](self.context, 0, None)
		self.vertex_count = name_type_map['Ubyte'](self.context, 0, None)

		# determines if weights are used by this chunk
		self.weights_flag = name_type_map['WeightsFlagMalta'](self.context, 0, None)
		self.zero = name_type_map['Ubyte'](self.context, 0, None)
		if set_default:
			self.set_defaults()

	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'scale', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'pack_base', name_type_map['Float'], (0, None), (False, None), (None, None)
		yield 'vertex_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)
		yield 'vertex_count', name_type_map['Ubyte'], (0, None), (False, None), (None, None)
		yield 'weights_flag', name_type_map['WeightsFlag'], (0, None), (False, None), (lambda context: context.version <= 51, None)
		yield 'weights_flag', name_type_map['WeightsFlagMalta'], (0, None), (False, None), (lambda context: context.version >= 52, None)
		yield 'zero', name_type_map['Ubyte'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'scale', name_type_map['Float'], (0, None), (False, None)
		yield 'pack_base', name_type_map['Float'], (0, None), (False, None)
		yield 'vertex_offset', name_type_map['Uint'], (0, None), (False, None)
		yield 'vertex_count', name_type_map['Ubyte'], (0, None), (False, None)
		if instance.context.version <= 51:
			yield 'weights_flag', name_type_map['WeightsFlag'], (0, None), (False, None)
		if instance.context.version >= 52:
			yield 'weights_flag', name_type_map['WeightsFlagMalta'], (0, None), (False, None)
		yield 'zero', name_type_map['Ubyte'], (0, None), (False, None)

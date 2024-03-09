from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint
from nifgen.formats.nif.basic import Uint64
from nifgen.formats.nif.bitflagss.VertexAttribute import VertexAttribute


class BSVertexDesc(BasicBitfield):

	__name__ = 'BSVertexDesc'
	_storage = Uint64
	vertex_data_size = BitfieldMember(pos=0, mask=0xF, return_type=Uint.from_value)
	dynamic_vertex_size = BitfieldMember(pos=4, mask=0xF0, return_type=Uint.from_value)
	uv_1_offset = BitfieldMember(pos=8, mask=0xF00, return_type=Uint.from_value)
	uv_2_offset = BitfieldMember(pos=12, mask=0xF000, return_type=Uint.from_value)
	normal_offset = BitfieldMember(pos=16, mask=0xF0000, return_type=Uint.from_value)
	tangent_offset = BitfieldMember(pos=20, mask=0xF00000, return_type=Uint.from_value)
	color_offset = BitfieldMember(pos=24, mask=0xF000000, return_type=Uint.from_value)
	skinning_data_offset = BitfieldMember(pos=28, mask=0xF0000000, return_type=Uint.from_value)
	landscape_data_offset = BitfieldMember(pos=32, mask=0xF00000000, return_type=Uint.from_value)
	eye_data_offset = BitfieldMember(pos=36, mask=0xF000000000, return_type=Uint.from_value)
	unused_01 = BitfieldMember(pos=40, mask=0xF0000000000, return_type=Uint.from_value)
	vertex_attributes = BitfieldMember(pos=44, mask=0xFFF00000000000, return_type=VertexAttribute.from_value)

	def set_defaults(self):
		pass

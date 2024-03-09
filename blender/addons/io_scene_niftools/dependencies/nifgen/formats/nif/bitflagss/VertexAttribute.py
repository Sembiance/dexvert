from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class VertexAttribute(BasicBitfield):

	"""
	The bits of BSVertexDesc that describe the enabled vertex attributes.
	"""

	__name__ = 'VertexAttribute'
	_storage = Ushort
	VERTEX = 2 ** 0
	U_VS = 2 ** 1
	U_VS_2 = 2 ** 2
	NORMALS = 2 ** 3
	TANGENTS = 2 ** 4
	VERTEX_COLORS = 2 ** 5
	SKINNED = 2 ** 6
	LAND_DATA = 2 ** 7
	EYE_DATA = 2 ** 8
	INSTANCE = 2 ** 9
	FULL_PRECISION = 2 ** 10
	vertex = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	u_vs = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	u_vs_2 = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	normals = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	tangents = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	vertex_colors = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	skinned = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	land_data = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	eye_data = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	instance = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	full_precision = BitfieldMember(pos=10, mask=0x400, return_type=bool)

	def set_defaults(self):
		pass

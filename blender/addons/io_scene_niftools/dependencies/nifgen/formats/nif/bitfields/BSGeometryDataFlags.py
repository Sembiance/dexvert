from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Bool
from nifgen.formats.nif.basic import Ushort


class BSGeometryDataFlags(BasicBitfield):

	__name__ = 'BSGeometryDataFlags'
	_storage = Ushort
	has_uv = BitfieldMember(pos=0, mask=0x0001, return_type=Bool.from_value)
	havok_material = BitfieldMember(pos=6, mask=0x0FC0, return_type=Ushort.from_value)
	has_tangents = BitfieldMember(pos=12, mask=0x1000, return_type=Bool.from_value)

	def set_defaults(self):
		pass

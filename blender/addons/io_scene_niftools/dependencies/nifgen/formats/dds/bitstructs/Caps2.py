from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint


class Caps2(BasicBitfield):

	__name__ = 'Caps2'
	_storage = Uint
	reserved_1 = BitfieldMember(pos=0, mask=0x1ff, return_type=int)
	cubemap = BitfieldMember(pos=9, mask=0x200, return_type=int)
	cubemap_pos_x = BitfieldMember(pos=10, mask=0x400, return_type=int)
	cubemap_neg_x = BitfieldMember(pos=11, mask=0x800, return_type=int)
	cubemap_pos_y = BitfieldMember(pos=12, mask=0x1000, return_type=int)
	cubemap_neg_y = BitfieldMember(pos=13, mask=0x2000, return_type=int)
	cubemap_pos_z = BitfieldMember(pos=14, mask=0x4000, return_type=int)
	cubemap_neg_z = BitfieldMember(pos=15, mask=0x8000, return_type=int)
	reserved_2 = BitfieldMember(pos=16, mask=0x1f0000, return_type=int)
	volume = BitfieldMember(pos=21, mask=0x200000, return_type=int)

	def set_defaults(self):
		pass

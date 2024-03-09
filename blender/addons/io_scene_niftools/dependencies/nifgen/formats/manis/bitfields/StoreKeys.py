from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Ubyte
from nifgen.formats.ovl_base.basic import Bool


class StoreKeys(BasicBitfield):

	__name__ = 'StoreKeys'
	_storage = Ubyte
	x = BitfieldMember(pos=0, mask=0x1, return_type=Bool.from_value)
	y = BitfieldMember(pos=1, mask=0x2, return_type=Bool.from_value)
	z = BitfieldMember(pos=2, mask=0x4, return_type=Bool.from_value)

	def set_defaults(self):
		pass

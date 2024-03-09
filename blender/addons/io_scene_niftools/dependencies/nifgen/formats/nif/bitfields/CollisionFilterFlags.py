from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Bool
from nifgen.formats.nif.basic import Byte
from nifgen.formats.nif.enums.BipedPart import BipedPart


class CollisionFilterFlags(BasicBitfield):

	__name__ = 'CollisionFilterFlags'
	_storage = Byte
	biped_part = BitfieldMember(pos=0, mask=0x001F, return_type=BipedPart.from_value)
	mopp_scaled = BitfieldMember(pos=5, mask=0x0020, return_type=Bool.from_value)
	no_collision = BitfieldMember(pos=6, mask=0x0040, return_type=Bool.from_value)
	linked_group = BitfieldMember(pos=7, mask=0x0080, return_type=Bool.from_value)

	def set_defaults(self):
		pass

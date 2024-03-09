from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint


class AnimationFlags(BasicBitfield):

	__name__ = 'AnimationFlags'
	_storage = Uint
	looping = BitfieldMember(pos=0, mask=0x1, return_type=int)
	additive = BitfieldMember(pos=1, mask=0x2, return_type=int)
	mirrored = BitfieldMember(pos=2, mask=0x4, return_type=int)
	affects_motion = BitfieldMember(pos=3, mask=0x8, return_type=int)
	flag_on_loop = BitfieldMember(pos=4, mask=0x10, return_type=int)
	reset_random_on_loop = BitfieldMember(pos=5, mask=0x20, return_type=int)
	suppress_resource_data_streams = BitfieldMember(pos=6, mask=0x40, return_type=int)

	def set_defaults(self):
		pass

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class NxMaterialFlag(BasicBitfield):

	__name__ = 'NxMaterialFlag'
	_storage = Uint
	ANISOTROPIC = 2 ** 0
	DISABLE_FRICTION = 2 ** 4
	DISABLE_STRONG_FRICTION = 2 ** 5
	anisotropic = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	disable_friction = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	disable_strong_friction = BitfieldMember(pos=5, mask=0x20, return_type=bool)

	def set_defaults(self):
		pass

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class NxClothFlag(BasicBitfield):

	__name__ = 'NxClothFlag'
	_storage = Uint
	PRESSURE = 2 ** 0
	STATIC = 2 ** 1
	DISABLE_COLLISION = 2 ** 2
	SELFCOLLISION = 2 ** 3
	VISUALIZATION = 2 ** 4
	GRAVITY = 2 ** 5
	BENDING = 2 ** 6
	BENDING_ORTHO = 2 ** 7
	DAMPING = 2 ** 8
	COLLISION_TWOWAY = 2 ** 9
	TRIANGLE_COLLISION = 2 ** 11
	TEARABLE = 2 ** 12
	HARDWARE = 2 ** 13
	COMDAMPING = 2 ** 14
	VALIDBOUNDS = 2 ** 15
	FLUID_COLLISION = 2 ** 16
	DISABLE_DYNAMIC_CCD = 2 ** 17
	ADHERE = 2 ** 18
	pressure = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	static = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	disable_collision = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	selfcollision = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	visualization = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	gravity = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	bending = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	bending_ortho = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	damping = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	collision_twoway = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	triangle_collision = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	tearable = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	hardware = BitfieldMember(pos=13, mask=0x2000, return_type=bool)
	comdamping = BitfieldMember(pos=14, mask=0x4000, return_type=bool)
	validbounds = BitfieldMember(pos=15, mask=0x8000, return_type=bool)
	fluid_collision = BitfieldMember(pos=16, mask=0x10000, return_type=bool)
	disable_dynamic_ccd = BitfieldMember(pos=17, mask=0x20000, return_type=bool)
	adhere = BitfieldMember(pos=18, mask=0x40000, return_type=bool)

	def set_defaults(self):
		pass

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class NxShapeFlag(BasicBitfield):

	__name__ = 'NxShapeFlag'
	_storage = Uint
	TRIGGER_ON_ENTER = 2 ** 0
	TRIGGER_ON_LEAVE = 2 ** 1
	TRIGGER_ON_STAY = 2 ** 2
	VISUALIZATION = 2 ** 3
	DISABLE_COLLISION = 2 ** 4
	FEATURE_INDICES = 2 ** 5
	DISABLE_RAYCASTING = 2 ** 6
	POINT_CONTACT_FORCE = 2 ** 7
	FLUID_DRAIN = 2 ** 8
	FLUID_DISABLE_COLLISION = 2 ** 10
	FLUID_TWOWAY = 2 ** 11
	DISABLE_RESPONSE = 2 ** 12
	DYNAMIC_DYNAMIC_CCD = 2 ** 13
	DISABLE_SCENE_QUERIES = 2 ** 14
	CLOTH_DRAIN = 2 ** 15
	CLOTH_DISABLE_COLLISION = 2 ** 16
	CLOTH_TWOWAY = 2 ** 17
	SOFTBODY_DRAIN = 2 ** 18
	SOFTBODY_DISABLE_COLLISION = 2 ** 19
	SOFTBODY_TWOWAY = 2 ** 20
	trigger_on_enter = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	trigger_on_leave = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	trigger_on_stay = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	visualization = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	disable_collision = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	feature_indices = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	disable_raycasting = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	point_contact_force = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	fluid_drain = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	fluid_disable_collision = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	fluid_twoway = BitfieldMember(pos=11, mask=0x800, return_type=bool)
	disable_response = BitfieldMember(pos=12, mask=0x1000, return_type=bool)
	dynamic_dynamic_ccd = BitfieldMember(pos=13, mask=0x2000, return_type=bool)
	disable_scene_queries = BitfieldMember(pos=14, mask=0x4000, return_type=bool)
	cloth_drain = BitfieldMember(pos=15, mask=0x8000, return_type=bool)
	cloth_disable_collision = BitfieldMember(pos=16, mask=0x10000, return_type=bool)
	cloth_twoway = BitfieldMember(pos=17, mask=0x20000, return_type=bool)
	softbody_drain = BitfieldMember(pos=18, mask=0x40000, return_type=bool)
	softbody_disable_collision = BitfieldMember(pos=19, mask=0x80000, return_type=bool)
	softbody_twoway = BitfieldMember(pos=20, mask=0x100000, return_type=bool)

	def set_defaults(self):
		pass

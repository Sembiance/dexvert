from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class BhkCOFlags(BasicBitfield):

	"""
	bhkNiCollisionObject flags.
	0x100 and 0x200 are only for bhkBlendCollisionObject
	"""

	__name__ = 'bhkCOFlags'
	_storage = Ushort
	ACTIVE = 2 ** 0
	RESET_TRANS = 2 ** 1
	NOTIFY = 2 ** 2
	SET_LOCAL = 2 ** 3
	DBG_DISPLAY = 2 ** 4
	USE_VEL = 2 ** 5
	RESET = 2 ** 6
	SYNC_ON_UPDATE = 2 ** 7
	BLEND_POS = 2 ** 8
	ALWAYS_BLEND = 2 ** 9
	ANIM_TARGETED = 2 ** 10
	DISMEMBERED_LIMB = 2 ** 11
	active = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	reset_trans = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	notify = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	set_local = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	dbg_display = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	use_vel = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	reset = BitfieldMember(pos=6, mask=0x40, return_type=bool)
	sync_on_update = BitfieldMember(pos=7, mask=0x80, return_type=bool)
	blend_pos = BitfieldMember(pos=8, mask=0x100, return_type=bool)
	always_blend = BitfieldMember(pos=9, mask=0x200, return_type=bool)
	anim_targeted = BitfieldMember(pos=10, mask=0x400, return_type=bool)
	dismembered_limb = BitfieldMember(pos=11, mask=0x800, return_type=bool)

	def set_defaults(self):
		pass

from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class FurnitureEntryPoints(BasicBitfield):

	"""
	Bethesda Animation. Furniture entry points. It specifies the direction(s) from where the actor is able to enter (and leave) the position.
	"""

	__name__ = 'FurnitureEntryPoints'
	_storage = Ushort
	FRONT = 2 ** 0
	BEHIND = 2 ** 1
	RIGHT = 2 ** 2
	LEFT = 2 ** 3
	UP = 2 ** 4
	front = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	behind = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	right = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	left = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	up = BitfieldMember(pos=4, mask=0x10, return_type=bool)

	def set_defaults(self):
		pass

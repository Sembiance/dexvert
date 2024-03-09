from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort


class BSPartFlag(BasicBitfield):

	"""
	Editor flags for the Body Partitions.
	"""

	__name__ = 'BSPartFlag'
	_storage = Ushort
	PF_EDITOR_VISIBLE = 2 ** 0
	PF_START_NET_BONESET = 2 ** 8
	pf_editor_visible = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	pf_start_net_boneset = BitfieldMember(pos=8, mask=0x100, return_type=bool)

	def set_defaults(self):
		pass

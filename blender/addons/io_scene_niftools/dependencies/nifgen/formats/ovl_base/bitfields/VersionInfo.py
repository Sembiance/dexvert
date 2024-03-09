from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.base.basic import Uint
from nifgen.formats.ovl_base.basic import Bool
from nifgen.formats.ovl_base.enums.Compression import Compression


class VersionInfo(BasicBitfield):

	"""
	Determines the format of the OVL file.
	n.b. pos counts from the end!
	# compression                         __ _
	# pc/pz uncompressed	8212	00100000 00010100
	# pc/pz zlib			8340	00100000 10010100
	# pc/pz oodle			8724	00100010 00010100
	
	# JWE (uncomp)	        24596	01100000 00010100
	# JWE zlib				24724	01100000 10010100
	# JWE oodle (switch)	25108	01100010 00010100
	"""

	__name__ = 'VersionInfo'
	_storage = Uint
	unk_1 = BitfieldMember(pos=2, mask=0x4, return_type=Bool.from_value)
	unk_2 = BitfieldMember(pos=4, mask=0x10, return_type=Bool.from_value)
	compression = BitfieldMember(pos=7, mask=0x380, return_type=Compression.from_value)
	unk_3 = BitfieldMember(pos=13, mask=0x2000, return_type=Bool.from_value)
	use_djb = BitfieldMember(pos=14, mask=0x4000, return_type=Bool.from_value)

	def set_defaults(self):
		pass

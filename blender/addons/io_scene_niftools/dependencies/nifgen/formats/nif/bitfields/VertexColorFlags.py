from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Ushort
from nifgen.formats.nif.enums.LightingMode import LightingMode
from nifgen.formats.nif.enums.SourceVertexMode import SourceVertexMode


class VertexColorFlags(BasicBitfield):

	"""
	Flags for NiVertexColorProperty
	"""

	__name__ = 'VertexColorFlags'
	_storage = Ushort
	color_mode = BitfieldMember(pos=0, mask=0x0007, return_type=Ushort.from_value)
	lighting_mode = BitfieldMember(pos=3, mask=0x0008, return_type=LightingMode.from_value)
	source_vertex_mode = BitfieldMember(pos=4, mask=0x0030, return_type=SourceVertexMode.from_value)

	def set_defaults(self):
		pass

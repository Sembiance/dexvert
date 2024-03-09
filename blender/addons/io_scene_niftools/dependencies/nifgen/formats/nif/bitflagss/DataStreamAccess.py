from nifgen.bitfield import BasicBitfield
from nifgen.bitfield import BitfieldMember
from nifgen.formats.nif.basic import Uint


class DataStreamAccess(BasicBitfield):

	"""
	Determines how the data stream is accessed?
	"""

	__name__ = 'DataStreamAccess'
	_storage = Uint
	CPU_READ = 2 ** 0
	CPU_WRITE_STATIC = 2 ** 1
	CPU_WRITE_MUTABLE = 2 ** 2
	CPU_WRITE_VOLATILE = 2 ** 3
	GPU_READ = 2 ** 4
	GPU_WRITE = 2 ** 5
	CPU_WRITE_STATIC_INITITIALIZED = 2 ** 6
	cpu_read = BitfieldMember(pos=0, mask=0x1, return_type=bool)
	cpu_write_static = BitfieldMember(pos=1, mask=0x2, return_type=bool)
	cpu_write_mutable = BitfieldMember(pos=2, mask=0x4, return_type=bool)
	cpu_write_volatile = BitfieldMember(pos=3, mask=0x8, return_type=bool)
	gpu_read = BitfieldMember(pos=4, mask=0x10, return_type=bool)
	gpu_write = BitfieldMember(pos=5, mask=0x20, return_type=bool)
	cpu_write_static_inititialized = BitfieldMember(pos=6, mask=0x40, return_type=bool)

	def set_defaults(self):
		pass

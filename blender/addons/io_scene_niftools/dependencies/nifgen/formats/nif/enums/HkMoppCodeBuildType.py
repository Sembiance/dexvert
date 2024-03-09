from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class HkMoppCodeBuildType(BaseEnum):

	"""
	hkpMoppCode::BuildType
	A byte describing if MOPP Data is organized into chunks (PS3) or not (PC)
	"""

	__name__ = 'hkMoppCodeBuildType'
	_storage = Byte


	# Organized in chunks for PS3.
	BUILT_WITH_CHUNK_SUBDIVISION = 0

	# Not organized in chunks for PC. (Default)
	BUILT_WITHOUT_CHUNK_SUBDIVISION = 1

	# Build type not set yet.
	BUILD_NOT_SET = 2

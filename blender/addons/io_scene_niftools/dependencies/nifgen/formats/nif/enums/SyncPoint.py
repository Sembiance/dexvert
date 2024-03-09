from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class SyncPoint(BaseEnum):

	"""
	A sync point corresponds to a particular stage in per-frame processing.
	"""

	__name__ = 'SyncPoint'
	_storage = Ushort


	# Synchronize for any sync points that the modifier supports.
	SYNC_ANY = 0x8000

	# Synchronize when an object is updated.
	SYNC_UPDATE = 0x8010

	# Synchronize when an entire scene graph has been updated.
	SYNC_POST_UPDATE = 0x8020

	# Synchronize when an object is determined to be potentially visible.
	SYNC_VISIBLE = 0x8030

	# Synchronize when an object is rendered.
	SYNC_RENDER = 0x8040

	# Synchronize when a physics simulation step is about to begin.
	SYNC_PHYSICS_SIMULATE = 0x8050

	# Synchronize when a physics simulation step has produced results.
	SYNC_PHYSICS_COMPLETED = 0x8060

	# Synchronize after all data necessary to calculate reflections is ready.
	SYNC_REFLECTIONS = 0x8070

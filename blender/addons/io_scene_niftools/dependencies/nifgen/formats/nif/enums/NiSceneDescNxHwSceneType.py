from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class NiSceneDescNxHwSceneType(BaseEnum):

	__name__ = 'NiSceneDescNxHwSceneType'
	_storage = Uint

	SCENE_TYPE_RB = 0
	SCENE_TYPE_FLUID = 1
	SCENE_TYPE_FLUID_SOFTWARE = 2
	SCENE_TYPE_CLOTH = 3

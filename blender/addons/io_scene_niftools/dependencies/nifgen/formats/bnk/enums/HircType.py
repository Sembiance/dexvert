from nifgen.base_enum import BaseEnum
from nifgen.formats.base.basic import Ubyte


class HircType(BaseEnum):

	__name__ = 'HircType'
	_storage = Ubyte

	NONE = 0
	SETTINGS = 1
	SOUND_SFX_VOICE = 2
	EVENT_ACTION = 3
	EVENT = 4
	RANDOM_OR_SEQUENCE_CONTAINER = 5
	SWITCH_CONTAINER = 6
	ACTOR_MIXER = 7
	AUDIO_BUS = 8
	BLEND_CONTAINER = 9
	MUSIC_SEGMENT = 10
	MUSIC_TRACK = 11
	MUSIC_SWITCH_CONTAINER = 12
	MUSIC_PLAYLIST_CONTAINER = 13
	ATTENUATION = 14
	DIALOGUE_EVENT = 15
	MOTION_BUS = 16
	MOTION_F_X = 17
	EFFECT = 18
	UNK_TYPE_19 = 19
	AUXILIARY_BUS = 20
	UNK_TYPE_21 = 21
	UNK_TYPE_22 = 22

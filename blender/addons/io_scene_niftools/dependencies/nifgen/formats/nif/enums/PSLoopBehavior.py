from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class PSLoopBehavior(BaseEnum):

	__name__ = 'PSLoopBehavior'
	_storage = Uint


	# Key times map such that the first key occurs at the birth of the particle, and times later than the last key get the last key value.
	PS_LOOP_CLAMP_BIRTH = 0

	# Key times map such that the last key occurs at the death of the particle, and times before the initial key time get the value of the initial key.
	PS_LOOP_CLAMP_DEATH = 1

	# Scale the animation to fit the particle lifetime, so that the first key is age zero, and the last key comes at the particle death.
	PS_LOOP_AGESCALE = 2

	# The time is converted to one within the time range represented by the keys, as if the key sequence loops forever in the past and future.
	PS_LOOP_LOOP = 3

	# The time is reflection looped, as if the keys played forward then backward the forward then backward etc for all time.
	PS_LOOP_REFLECT = 4

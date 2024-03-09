from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class BipedPart(BaseEnum):

	__name__ = 'BipedPart'
	_storage = Byte


	# Other
	P_OTHER = 0

	# Head
	P_HEAD = 1

	# Body
	P_BODY = 2

	# Spine1
	P_SPINE1 = 3

	# Spine2
	P_SPINE2 = 4

	# LUpperArm
	P_L_UPPER_ARM = 5

	# LForeArm
	P_L_FOREARM = 6

	# LHand
	P_L_HAND = 7

	# LThigh
	P_L_THIGH = 8

	# LCalf
	P_L_CALF = 9

	# LFoot
	P_L_FOOT = 10

	# RUpperArm
	P_R_UPPER_ARM = 11

	# RForeArm
	P_R_FOREARM = 12

	# RHand
	P_R_HAND = 13

	# RThigh
	P_R_THIGH = 14

	# RCalf
	P_R_CALF = 15

	# RFoot
	P_R_FOOT = 16

	# Tail
	P_TAIL = 17

	# Shield
	P_SHIELD = 18

	# Quiver
	P_QUIVER = 19

	# Weapon
	P_WEAPON = 20

	# Ponytail
	P_PONYTAIL = 21

	# Wing
	P_WING = 22

	# Pack
	P_PACK = 23

	# Chain
	P_CHAIN = 24

	# AddonHead
	P_ADDON_HEAD = 25

	# AddonChest
	P_ADDON_CHEST = 26

	# AddonLeg
	P_ADDON_LEG = 27

	# AddonArm
	P_ADDON_ARM = 28

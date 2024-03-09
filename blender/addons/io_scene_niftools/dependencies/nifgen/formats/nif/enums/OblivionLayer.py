from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class OblivionLayer(BaseEnum):

	"""
	Bethesda Havok. Describes the collision layer a body belongs to in Oblivion.
	"""

	__name__ = 'OblivionLayer'
	_storage = Byte


	# Unidentified (white)
	OL_UNIDENTIFIED = 0

	# Static (red)
	OL_STATIC = 1

	# AnimStatic (magenta)
	OL_ANIM_STATIC = 2

	# Transparent (light pink)
	OL_TRANSPARENT = 3

	# Clutter (light blue)
	OL_CLUTTER = 4

	# Weapon (orange)
	OL_WEAPON = 5

	# Projectile (light orange)
	OL_PROJECTILE = 6

	# Spell (cyan)
	OL_SPELL = 7

	# Biped (green) Seems to apply to all creatures/NPCs
	OL_BIPED = 8

	# Trees (light brown)
	OL_TREES = 9

	# Props (magenta)
	OL_PROPS = 10

	# Water (cyan)
	OL_WATER = 11

	# Trigger (light grey)
	OL_TRIGGER = 12

	# Terrain (light yellow)
	OL_TERRAIN = 13

	# Trap (light grey)
	OL_TRAP = 14

	# NonCollidable (white)
	OL_NONCOLLIDABLE = 15

	# CloudTrap (greenish grey)
	OL_CLOUD_TRAP = 16

	# Ground (none)
	OL_GROUND = 17

	# Portal (green)
	OL_PORTAL = 18

	# Stairs (white)
	OL_STAIRS = 19

	# CharController (yellow)
	OL_CHAR_CONTROLLER = 20

	# AvoidBox (dark yellow)
	OL_AVOID_BOX = 21

	# ? (white)
	OL_UNKNOWN1 = 22

	# ? (white)
	OL_UNKNOWN2 = 23

	# CameraPick (white)
	OL_CAMERA_PICK = 24

	# ItemPick (white)
	OL_ITEM_PICK = 25

	# LineOfSight (white)
	OL_LINE_OF_SIGHT = 26

	# PathPick (white)
	OL_PATH_PICK = 27

	# CustomPick1 (white)
	OL_CUSTOM_PICK_1 = 28

	# CustomPick2 (white)
	OL_CUSTOM_PICK_2 = 29

	# SpellExplosion (white)
	OL_SPELL_EXPLOSION = 30

	# DroppingPick (white)
	OL_DROPPING_PICK = 31

	# Other (white)
	OL_OTHER = 32

	# Head
	OL_HEAD = 33

	# Body
	OL_BODY = 34

	# Spine1
	OL_SPINE1 = 35

	# Spine2
	OL_SPINE2 = 36

	# LUpperArm
	OL_L_UPPER_ARM = 37

	# LForeArm
	OL_L_FOREARM = 38

	# LHand
	OL_L_HAND = 39

	# LThigh
	OL_L_THIGH = 40

	# LCalf
	OL_L_CALF = 41

	# LFoot
	OL_L_FOOT = 42

	# RUpperArm
	OL_R_UPPER_ARM = 43

	# RForeArm
	OL_R_FOREARM = 44

	# RHand
	OL_R_HAND = 45

	# RThigh
	OL_R_THIGH = 46

	# RCalf
	OL_R_CALF = 47

	# RFoot
	OL_R_FOOT = 48

	# Tail
	OL_TAIL = 49

	# SideWeapon
	OL_SIDE_WEAPON = 50

	# Shield
	OL_SHIELD = 51

	# Quiver
	OL_QUIVER = 52

	# BackWeapon
	OL_BACK_WEAPON = 53

	# BackWeapon (?)
	OL_BACK_WEAPON2 = 54

	# PonyTail
	OL_PONYTAIL = 55

	# Wing
	OL_WING = 56

	# Null
	OL_NULL = 57

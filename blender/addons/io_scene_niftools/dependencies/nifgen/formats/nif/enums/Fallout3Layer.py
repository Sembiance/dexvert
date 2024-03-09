from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class Fallout3Layer(BaseEnum):

	"""
	Bethesda Havok. Describes the collision layer a body belongs to in Fallout 3 and Fallout NV.
	"""

	__name__ = 'Fallout3Layer'
	_storage = Byte


	# Unidentified (white)
	FOL_UNIDENTIFIED = 0

	# Static (red)
	FOL_STATIC = 1

	# AnimStatic (magenta)
	FOL_ANIM_STATIC = 2

	# Transparent (light pink)
	FOL_TRANSPARENT = 3

	# Clutter (light blue)
	FOL_CLUTTER = 4

	# Weapon (orange)
	FOL_WEAPON = 5

	# Projectile (light orange)
	FOL_PROJECTILE = 6

	# Spell (cyan)
	FOL_SPELL = 7

	# Biped (green) Seems to apply to all creatures/NPCs
	FOL_BIPED = 8

	# Trees (light brown)
	FOL_TREES = 9

	# Props (magenta)
	FOL_PROPS = 10

	# Water (cyan)
	FOL_WATER = 11

	# Trigger (light grey)
	FOL_TRIGGER = 12

	# Terrain (light yellow)
	FOL_TERRAIN = 13

	# Trap (light grey)
	FOL_TRAP = 14

	# NonCollidable (white)
	FOL_NONCOLLIDABLE = 15

	# CloudTrap (greenish grey)
	FOL_CLOUD_TRAP = 16

	# Ground (none)
	FOL_GROUND = 17

	# Portal (green)
	FOL_PORTAL = 18

	# DebrisSmall (white)
	FOL_DEBRIS_SMALL = 19

	# DebrisLarge (white)
	FOL_DEBRIS_LARGE = 20

	# AcousticSpace (white)
	FOL_ACOUSTIC_SPACE = 21

	# Actorzone (white)
	FOL_ACTORZONE = 22

	# Projectilezone (white)
	FOL_PROJECTILEZONE = 23

	# GasTrap (yellowish green)
	FOL_GASTRAP = 24

	# ShellCasing (white)
	FOL_SHELLCASING = 25

	# TransparentSmall (white)
	FOL_TRANSPARENT_SMALL = 26

	# InvisibleWall (white)
	FOL_INVISIBLE_WALL = 27

	# TransparentSmallAnim (white)
	FOL_TRANSPARENT_SMALL_ANIM = 28

	# Dead Biped (green)
	FOL_DEADBIP = 29

	# CharController (yellow)
	FOL_CHARCONTROLLER = 30

	# Avoidbox (orange)
	FOL_AVOIDBOX = 31

	# Collisionbox (white)
	FOL_COLLISIONBOX = 32

	# Camerasphere (white)
	FOL_CAMERASPHERE = 33

	# Doordetection (white)
	FOL_DOORDETECTION = 34

	# Camerapick (white)
	FOL_CAMERAPICK = 35

	# Itempick (white)
	FOL_ITEMPICK = 36

	# LineOfSight (white)
	FOL_LINEOFSIGHT = 37

	# Pathpick (white)
	FOL_PATHPICK = 38

	# Custompick1 (white)
	FOL_CUSTOMPICK1 = 39

	# Custompick2 (white)
	FOL_CUSTOMPICK2 = 40

	# SpellExplosion (white)
	FOL_SPELLEXPLOSION = 41

	# Droppingpick (white)
	FOL_DROPPINGPICK = 42

	# Null (white)
	FOL_NULL = 43

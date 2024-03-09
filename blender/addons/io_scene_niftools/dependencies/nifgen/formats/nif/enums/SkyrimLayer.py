from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class SkyrimLayer(BaseEnum):

	"""
	Bethesda Havok. Describes the collision layer a body belongs to in Skyrim.
	"""

	__name__ = 'SkyrimLayer'
	_storage = Byte


	# Unidentified
	SKYL_UNIDENTIFIED = 0

	# Static
	SKYL_STATIC = 1

	# Anim Static
	SKYL_ANIMSTATIC = 2

	# Transparent
	SKYL_TRANSPARENT = 3

	# Clutter. Object with this layer will float on water surface.
	SKYL_CLUTTER = 4

	# Weapon
	SKYL_WEAPON = 5

	# Projectile
	SKYL_PROJECTILE = 6

	# Spell
	SKYL_SPELL = 7

	# Biped. Seems to apply to all creatures/NPCs
	SKYL_BIPED = 8

	# Trees
	SKYL_TREES = 9

	# Props
	SKYL_PROPS = 10

	# Water
	SKYL_WATER = 11

	# Trigger
	SKYL_TRIGGER = 12

	# Terrain
	SKYL_TERRAIN = 13

	# Trap
	SKYL_TRAP = 14

	# NonCollidable
	SKYL_NONCOLLIDABLE = 15

	# CloudTrap
	SKYL_CLOUD_TRAP = 16

	# Ground. It seems that produces no sound when collide.
	SKYL_GROUND = 17

	# Portal
	SKYL_PORTAL = 18

	# Debris Small
	SKYL_DEBRIS_SMALL = 19

	# Debris Large
	SKYL_DEBRIS_LARGE = 20

	# Acoustic Space
	SKYL_ACOUSTIC_SPACE = 21

	# Actor Zone
	SKYL_ACTORZONE = 22

	# Projectile Zone
	SKYL_PROJECTILEZONE = 23

	# Gas Trap
	SKYL_GASTRAP = 24

	# Shell Casing
	SKYL_SHELLCASING = 25

	# Transparent Small
	SKYL_TRANSPARENT_SMALL = 26

	# Invisible Wall
	SKYL_INVISIBLE_WALL = 27

	# Transparent Small Anim
	SKYL_TRANSPARENT_SMALL_ANIM = 28

	# Ward
	SKYL_WARD = 29

	# Char Controller
	SKYL_CHARCONTROLLER = 30

	# Stair Helper
	SKYL_STAIRHELPER = 31

	# Dead Bip
	SKYL_DEADBIP = 32

	# Biped No CC
	SKYL_BIPED_NO_CC = 33

	# Avoid Box
	SKYL_AVOIDBOX = 34

	# Collision Box
	SKYL_COLLISIONBOX = 35

	# Camera Sphere
	SKYL_CAMERASHPERE = 36

	# Door Detection
	SKYL_DOORDETECTION = 37

	# Cone Projectile
	SKYL_CONEPROJECTILE = 38

	# Camera Pick
	SKYL_CAMERAPICK = 39

	# Item Pick
	SKYL_ITEMPICK = 40

	# Line of Sight
	SKYL_LINEOFSIGHT = 41

	# Path Pick
	SKYL_PATHPICK = 42

	# Custom Pick 1
	SKYL_CUSTOMPICK1 = 43

	# Custom Pick 2
	SKYL_CUSTOMPICK2 = 44

	# Spell Explosion
	SKYL_SPELLEXPLOSION = 45

	# Dropping Pick
	SKYL_DROPPINGPICK = 46

	# Dead Actor Zone
	SKYL_DEADACTORZONE = 47

	# Falling Trap Trigger
	SKYL_TRIGGER_FALLINGTRAP = 48

	# Nav Cut
	SKYL_NAVCUT = 49

	# Critter
	SKYL_CRITTER = 50

	# Spell Trigger
	SKYL_SPELLTRIGGER = 51

	# Living And Dead Actors
	SKYL_LIVING_AND_DEAD_ACTORS = 52

	# Detection
	SKYL_DETECTION = 53

	# Trap Trigger
	SKYL_TRAP_TRIGGER = 54

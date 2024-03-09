from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Byte


class HkQualityType(BaseEnum):

	"""
	hkpCollidableQualityType. Describes the priority and quality of collisions for a body,
	e.g. you may expect critical game play objects to have solid high-priority collisions so that they never sink into ground,
	or may allow penetrations for visual debris objects.
	Notes:
	- Fixed and keyframed objects cannot interact with each other.
	- Debris can interpenetrate but still responds to Bullet hits.
	- Critical objects are forced to not interpenetrate.
	- Moving objects can interpenetrate slightly with other Moving or Debris objects but nothing else.
	"""

	__name__ = 'hkQualityType'
	_storage = Byte


	# Automatically assigned to MO_QUAL_FIXED, MO_QUAL_KEYFRAMED or MO_QUAL_DEBRIS
	MO_QUAL_INVALID = 0

	# Static body.
	MO_QUAL_FIXED = 1

	# Animated body with infinite mass.
	MO_QUAL_KEYFRAMED = 2

	# Low importance bodies adding visual detail.
	MO_QUAL_DEBRIS = 3

	# Moving bodies which should not penetrate or leave the world, but can.
	MO_QUAL_MOVING = 4

	# Gameplay critical bodies which cannot penetrate or leave the world under any circumstance.
	MO_QUAL_CRITICAL = 5

	# Fast-moving bodies, such as projectiles.
	MO_QUAL_BULLET = 6

	# For user.
	MO_QUAL_USER = 7

	# For use with rigid body character controllers.
	MO_QUAL_CHARACTER = 8

	# Moving bodies with infinite mass which should report contact points and TOI collisions against all other bodies.
	MO_QUAL_KEYFRAMED_REPORT = 9

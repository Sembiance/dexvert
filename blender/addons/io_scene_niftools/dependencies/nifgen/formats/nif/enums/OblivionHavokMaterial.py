from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class OblivionHavokMaterial(BaseEnum):

	"""
	Bethesda Havok. Material descriptor for a Havok shape in Oblivion.
	"""

	__name__ = 'OblivionHavokMaterial'
	_storage = Uint


	# Stone
	OB_HAV_MAT_STONE = 0

	# Cloth
	OB_HAV_MAT_CLOTH = 1

	# Dirt
	OB_HAV_MAT_DIRT = 2

	# Glass
	OB_HAV_MAT_GLASS = 3

	# Grass
	OB_HAV_MAT_GRASS = 4

	# Metal
	OB_HAV_MAT_METAL = 5

	# Organic
	OB_HAV_MAT_ORGANIC = 6

	# Skin
	OB_HAV_MAT_SKIN = 7

	# Water
	OB_HAV_MAT_WATER = 8

	# Wood
	OB_HAV_MAT_WOOD = 9

	# Heavy Stone
	OB_HAV_MAT_HEAVY_STONE = 10

	# Heavy Metal
	OB_HAV_MAT_HEAVY_METAL = 11

	# Heavy Wood
	OB_HAV_MAT_HEAVY_WOOD = 12

	# Chain
	OB_HAV_MAT_CHAIN = 13

	# Snow
	OB_HAV_MAT_SNOW = 14

	# Stone Stairs
	OB_HAV_MAT_STONE_STAIRS = 15

	# Cloth Stairs
	OB_HAV_MAT_CLOTH_STAIRS = 16

	# Dirt Stairs
	OB_HAV_MAT_DIRT_STAIRS = 17

	# Glass Stairs
	OB_HAV_MAT_GLASS_STAIRS = 18

	# Grass Stairs
	OB_HAV_MAT_GRASS_STAIRS = 19

	# Metal Stairs
	OB_HAV_MAT_METAL_STAIRS = 20

	# Organic Stairs
	OB_HAV_MAT_ORGANIC_STAIRS = 21

	# Skin Stairs
	OB_HAV_MAT_SKIN_STAIRS = 22

	# Water Stairs
	OB_HAV_MAT_WATER_STAIRS = 23

	# Wood Stairs
	OB_HAV_MAT_WOOD_STAIRS = 24

	# Heavy Stone Stairs
	OB_HAV_MAT_HEAVY_STONE_STAIRS = 25

	# Heavy Metal Stairs
	OB_HAV_MAT_HEAVY_METAL_STAIRS = 26

	# Heavy Wood Stairs
	OB_HAV_MAT_HEAVY_WOOD_STAIRS = 27

	# Chain Stairs
	OB_HAV_MAT_CHAIN_STAIRS = 28

	# Snow Stairs
	OB_HAV_MAT_SNOW_STAIRS = 29

	# Elevator
	OB_HAV_MAT_ELEVATOR = 30

	# Rubber
	OB_HAV_MAT_RUBBER = 31

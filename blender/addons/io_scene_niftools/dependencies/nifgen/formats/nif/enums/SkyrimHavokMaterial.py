from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Uint


class SkyrimHavokMaterial(BaseEnum):

	"""
	Bethesda Havok. Material descriptor for a Havok shape in Skyrim. CRC32 of the lowercase of the Creation Kit Material Name.
	"""

	__name__ = 'SkyrimHavokMaterial'
	_storage = Uint


	# Invalid Material
	SKY_HAV_MAT_NONE = 0

	# Broken Stone
	SKY_HAV_MAT_BROKEN_STONE = 131151687

	# Material Carriage Wheel
	SKY_HAV_MAT_MATERIAL_CARRIAGE_WHEEL = 322207473

	# Material Metal Light
	SKY_HAV_MAT_MATERIAL_METAL_LIGHT = 346811165

	# Light Wood
	SKY_HAV_MAT_LIGHT_WOOD = 365420259

	# Snow
	SKY_HAV_MAT_SNOW = 398949039

	# Gravel
	SKY_HAV_MAT_GRAVEL = 428587608

	# Material Chain Metal
	SKY_HAV_MAT_MATERIAL_CHAIN_METAL = 438912228

	# Bottle
	SKY_HAV_MAT_BOTTLE = 493553910

	# Wood
	SKY_HAV_MAT_WOOD = 500811281

	# Skin
	SKY_HAV_MAT_SKIN = 591247106

	# Unknown in Creation Kit v1.9.32.0. Found in Dawnguard DLC in meshes\dlc01\clutter\dlc01deerskin.nif.
	SKY_HAV_MAT_UNKNOWN_617099282 = 617099282

	# Barrel
	SKY_HAV_MAT_BARREL = 732141076

	# Material Ceramic Medium
	SKY_HAV_MAT_MATERIAL_CERAMIC_MEDIUM = 781661019

	# Material Basket
	SKY_HAV_MAT_MATERIAL_BASKET = 790784366

	# Ice
	SKY_HAV_MAT_ICE = 873356572

	# Stairs Glass
	SKY_HAV_MAT_STAIRS_GLASS = 880200008

	# Stairs Stone
	SKY_HAV_MAT_STAIRS_STONE = 899511101

	# Water
	SKY_HAV_MAT_WATER = 1024582599

	# Unknown in Creation Kit v1.6.89.0. Found in actors\draugr\character assets\skeletons.nif.
	SKY_HAV_MAT_UNKNOWN_1028101969 = 1028101969

	# Material Blade 1 Hand
	SKY_HAV_MAT_MATERIAL_BLADE_1HAND = 1060167844

	# Material Book
	SKY_HAV_MAT_MATERIAL_BOOK = 1264672850

	# Material Carpet
	SKY_HAV_MAT_MATERIAL_CARPET = 1286705471

	# Solid Metal
	SKY_HAV_MAT_SOLID_METAL = 1288358971

	# Material Axe 1Hand
	SKY_HAV_MAT_MATERIAL_AXE_1HAND = 1305674443

	# Unknown in Creation Kit v1.6.89.0. Found in armor\draugr\draugrbootsfemale_go.nif or armor\amuletsandrings\amuletgnd.nif.
	SKY_HAV_MAT_UNKNOWN_1440721808 = 1440721808

	# Stairs Wood
	SKY_HAV_MAT_STAIRS_WOOD = 1461712277

	# Mud
	SKY_HAV_MAT_MUD = 1486385281

	# Material Boulder Small
	SKY_HAV_MAT_MATERIAL_BOULDER_SMALL = 1550912982

	# Stairs Snow
	SKY_HAV_MAT_STAIRS_SNOW = 1560365355

	# Heavy Stone
	SKY_HAV_MAT_HEAVY_STONE = 1570821952

	# Unknown in Creation Kit v1.6.89.0. Found in actors\dragon\character assets\skeleton.nif.
	SKY_HAV_MAT_UNKNOWN_1574477864 = 1574477864

	# Unknown in Creation Kit v1.6.89.0. Found in trap objects or clutter\displaycases\displaycaselgangled01.nif or actors\deer\character assets\skeleton.nif.
	SKY_HAV_MAT_UNKNOWN_1591009235 = 1591009235

	# Material Bows Staves
	SKY_HAV_MAT_MATERIAL_BOWS_STAVES = 1607128641

	# Material Wood As Stairs
	SKY_HAV_MAT_MATERIAL_WOOD_AS_STAIRS = 1803571212

	# Grass
	SKY_HAV_MAT_GRASS = 1848600814

	# Material Boulder Large
	SKY_HAV_MAT_MATERIAL_BOULDER_LARGE = 1885326971

	# Material Stone As Stairs
	SKY_HAV_MAT_MATERIAL_STONE_AS_STAIRS = 1886078335

	# Material Blade 2Hand
	SKY_HAV_MAT_MATERIAL_BLADE_2HAND = 2022742644

	# Material Bottle Small
	SKY_HAV_MAT_MATERIAL_BOTTLE_SMALL = 2025794648

	# Sand
	SKY_HAV_MAT_SAND = 2168343821

	# Heavy Metal
	SKY_HAV_MAT_HEAVY_METAL = 2229413539

	# Unknown in Creation Kit v1.9.32.0. Found in Dawnguard DLC in meshes\dlc01\clutter\dlc01sabrecatpelt.nif.
	SKY_HAV_MAT_UNKNOWN_2290050264 = 2290050264

	# Dragon
	SKY_HAV_MAT_DRAGON = 2518321175

	# Material Blade 1Hand Small
	SKY_HAV_MAT_MATERIAL_BLADE_1HAND_SMALL = 2617944780

	# Material Skin Small
	SKY_HAV_MAT_MATERIAL_SKIN_SMALL = 2632367422

	# Material Pots Pans
	SKY_HAV_MAT_MATERIAL_POTS_PANS = 2742858142

	# Stairs Broken Stone
	SKY_HAV_MAT_STAIRS_BROKEN_STONE = 2892392795

	# Material Skin Large
	SKY_HAV_MAT_MATERIAL_SKIN_LARGE = 2965929619

	# Organic
	SKY_HAV_MAT_ORGANIC = 2974920155

	# Material Bone
	SKY_HAV_MAT_MATERIAL_BONE = 3049421844

	# Heavy Wood
	SKY_HAV_MAT_HEAVY_WOOD = 3070783559

	# Material Chain
	SKY_HAV_MAT_MATERIAL_CHAIN = 3074114406

	# Dirt
	SKY_HAV_MAT_DIRT = 3106094762

	# Material Skin Metal Large
	SKY_HAV_MAT_MATERIAL_SKIN_METAL_LARGE = 3387452107

	# Material Armor Light
	SKY_HAV_MAT_MATERIAL_ARMOR_LIGHT = 3424720541

	# Material Shield Light
	SKY_HAV_MAT_MATERIAL_SHIELD_LIGHT = 3448167928

	# Material Coin
	SKY_HAV_MAT_MATERIAL_COIN = 3589100606

	# Material Shield Heavy
	SKY_HAV_MAT_MATERIAL_SHIELD_HEAVY = 3702389584

	# Material Armor Heavy
	SKY_HAV_MAT_MATERIAL_ARMOR_HEAVY = 3708432437

	# Material Arrow
	SKY_HAV_MAT_MATERIAL_ARROW = 3725505938

	# Glass
	SKY_HAV_MAT_GLASS = 3739830338

	# Stone
	SKY_HAV_MAT_STONE = 3741512247

	# Material Water Puddle
	SKY_HAV_MAT_MATERIAL_WATER_PUDDLE = 3764646153

	# Cloth
	SKY_HAV_MAT_CLOTH = 3839073443

	# Material Skin Metal Small
	SKY_HAV_MAT_MATERIAL_SKIN_METAL_SMALL = 3855001958

	# Ward
	SKY_HAV_MAT_WARD = 3895166727

	# Web
	SKY_HAV_MAT_WEB = 3934839107

	# Material Blunt 2Hand
	SKY_HAV_MAT_MATERIAL_BLUNT_2HAND = 3969592277

	# Unknown in Creation Kit v1.9.32.0. Found in Dawnguard DLC in meshes\dlc01\prototype\dlc1protoswingingbridge.nif.
	SKY_HAV_MAT_UNKNOWN_4239621792 = 4239621792

	# Material Boulder Medium
	SKY_HAV_MAT_MATERIAL_BOULDER_MEDIUM = 4283869410
	SKY_HAV_MAT_UNKNOWN_2794252627 = 2794252627
	SKY_HAV_MAT_UNKNOWN_1668849266 = 1668849266
	SKY_HAV_MAT_UNKNOWN_1734341287 = 1734341287
	SKY_HAV_MAT_UNKNOWN_3974071006 = 3974071006

	# tfxsteelswordbloody
	SKY_HAV_MAT_UNKNOWN_3941234649 = 3941234649

	# steelgreatsword
	SKY_HAV_MAT_UNKNOWN_1820198263 = 1820198263

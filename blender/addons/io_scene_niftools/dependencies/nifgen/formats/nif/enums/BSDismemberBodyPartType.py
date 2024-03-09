from nifgen.base_enum import BaseEnum
from nifgen.formats.nif.basic import Ushort


class BSDismemberBodyPartType(BaseEnum):

	"""
	Biped bodypart data used for visibility control of triangles.  Options are Fallout 3, except where marked for Skyrim (uses SBP prefix)
	Skyrim BP names are listed only for vanilla names, different creatures have different defnitions for naming.
	"""

	__name__ = 'BSDismemberBodyPartType'
	_storage = Ushort


	# Torso
	BP_TORSO = 0

	# Head
	BP_HEAD = 1

	# Head 2
	BP_HEAD2 = 2

	# Left Arm
	BP_LEFTARM = 3

	# Left Arm 2
	BP_LEFTARM2 = 4

	# Right Arm
	BP_RIGHTARM = 5

	# Right Arm 2
	BP_RIGHTARM2 = 6

	# Left Leg
	BP_LEFTLEG = 7

	# Left Leg 2
	BP_LEFTLEG2 = 8

	# Left Leg 3
	BP_LEFTLEG3 = 9

	# Right Leg
	BP_RIGHTLEG = 10

	# Right Leg 2
	BP_RIGHTLEG2 = 11

	# Right Leg 3
	BP_RIGHTLEG3 = 12

	# Brain
	BP_BRAIN = 13

	# Skyrim, Head(Human), Body(Atronachs,Beasts), Mask(Dragonpriest)
	SBP_30_HEAD = 30

	# Skyrim, Hair(human), Far(Dragon), Mask2(Dragonpriest),SkinnedFX(Spriggan)
	SBP_31_HAIR = 31

	# Skyrim, Main body, extras(Spriggan)
	SBP_32_BODY = 32

	# Skyrim, Hands L/R, BodyToo(Dragonpriest), Legs(Draugr), Arms(Giant)
	SBP_33_HANDS = 33

	# Skyrim, Forearms L/R, Beard(Draugr)
	SBP_34_FOREARMS = 34

	# Skyrim, Amulet
	SBP_35_AMULET = 35

	# Skyrim, Ring
	SBP_36_RING = 36

	# Skyrim, Feet L/R
	SBP_37_FEET = 37

	# Skyrim, Calves L/R
	SBP_38_CALVES = 38

	# Skyrim, Shield
	SBP_39_SHIELD = 39

	# Skyrim, Tail(Argonian/Khajiit), Skeleton01(Dragon), FX01(AtronachStorm),FXMist (Dragonpriest), Spit(Chaurus,Spider),SmokeFins(IceWraith)
	SBP_40_TAIL = 40

	# Skyrim, Long Hair(Human), Skeleton02(Dragon),FXParticles(Dragonpriest)
	SBP_41_LONGHAIR = 41

	# Skyrim, Circlet(Human, MouthFireEffect(Dragon)
	SBP_42_CIRCLET = 42

	# Skyrim, Ears
	SBP_43_EARS = 43

	# Skyrim, Bloodied dragon head, or NPC face/mouth
	SBP_44_DRAGON_BLOODHEAD_OR_MOD_MOUTH = 44

	# Skyrim, Left Bloodied dragon wing, Saddle(Horse), or NPC cape, scarf, shawl, neck-tie, etc.
	SBP_45_DRAGON_BLOODWINGL_OR_MOD_NECK = 45

	# Skyrim, Right Bloodied dragon wing, or NPC chest primary or outergarment
	SBP_46_DRAGON_BLOODWINGR_OR_MOD_CHEST_PRIMARY = 46

	# Skyrim, Bloodied dragon tail, or NPC backpack/wings/...
	SBP_47_DRAGON_BLOODTAIL_OR_MOD_BACK = 47

	# Anything that does not fit in the list
	SBP_48_MOD_MISC1 = 48

	# Pelvis primary or outergarment
	SBP_49_MOD_PELVIS_PRIMARY = 49

	# Skyrim, Decapitated Head
	SBP_50_DECAPITATEDHEAD = 50

	# Skyrim, Decapitate, neck gore
	SBP_51_DECAPITATE = 51

	# Pelvis secondary or undergarment
	SBP_52_MOD_PELVIS_SECONDARY = 52

	# Leg primary or outergarment or right leg
	SBP_53_MOD_LEG_RIGHT = 53

	# Leg secondary or undergarment or left leg
	SBP_54_MOD_LEG_LEFT = 54

	# Face alternate or jewelry
	SBP_55_MOD_FACE_JEWELRY = 55

	# Chest secondary or undergarment
	SBP_56_MOD_CHEST_SECONDARY = 56

	# Shoulder
	SBP_57_MOD_SHOULDER = 57

	# Arm secondary or undergarment or left arm
	SBP_58_MOD_ARM_LEFT = 58

	# Arm primary or outergarment or right arm
	SBP_59_MOD_ARM_RIGHT = 59

	# Anything that does not fit in the list
	SBP_60_MOD_MISC2 = 60

	# Skyrim, FX01(Humanoid)
	SBP_61_FX01 = 61

	# Section Cap | Head
	BP_SECTIONCAP_HEAD = 101

	# Section Cap | Head 2
	BP_SECTIONCAP_HEAD2 = 102

	# Section Cap | Left Arm
	BP_SECTIONCAP_LEFTARM = 103

	# Section Cap | Left Arm 2
	BP_SECTIONCAP_LEFTARM2 = 104

	# Section Cap | Right Arm
	BP_SECTIONCAP_RIGHTARM = 105

	# Section Cap | Right Arm 2
	BP_SECTIONCAP_RIGHTARM2 = 106

	# Section Cap | Left Leg
	BP_SECTIONCAP_LEFTLEG = 107

	# Section Cap | Left Leg 2
	BP_SECTIONCAP_LEFTLEG2 = 108

	# Section Cap | Left Leg 3
	BP_SECTIONCAP_LEFTLEG3 = 109

	# Section Cap | Right Leg
	BP_SECTIONCAP_RIGHTLEG = 110

	# Section Cap | Right Leg 2
	BP_SECTIONCAP_RIGHTLEG2 = 111

	# Section Cap | Right Leg 3
	BP_SECTIONCAP_RIGHTLEG3 = 112

	# Section Cap | Brain
	BP_SECTIONCAP_BRAIN = 113

	# Skyrim, Head slot, use on full-face helmets
	SBP_130_HEAD = 130

	# Skyrim, Hair slot 1, use on hoods
	SBP_131_HAIR = 131

	# Skyrim, Hair slot 2?, use on hoods
	SBP_132_HAIR = 132

	# Skyrim, Hair slot 2, use for longer hair
	SBP_141_LONGHAIR = 141

	# Skyrim, Circlet slot 1, use for circlets
	SBP_142_CIRCLET = 142

	# Skyrim, Ear slot
	SBP_143_EARS = 143

	# Skyrim, neck gore on head side
	SBP_150_DECAPITATEDHEAD = 150

	# Torso Cap | Head
	BP_TORSOCAP_HEAD = 201

	# Torso Cap | Head 2
	BP_TORSOCAP_HEAD2 = 202

	# Torso Cap | Left Arm
	BP_TORSOCAP_LEFTARM = 203

	# Torso Cap | Left Arm 2
	BP_TORSOCAP_LEFTARM2 = 204

	# Torso Cap | Right Arm
	BP_TORSOCAP_RIGHTARM = 205

	# Torso Cap | Right Arm 2
	BP_TORSOCAP_RIGHTARM2 = 206

	# Torso Cap | Left Leg
	BP_TORSOCAP_LEFTLEG = 207

	# Torso Cap | Left Leg 2
	BP_TORSOCAP_LEFTLEG2 = 208

	# Torso Cap | Left Leg 3
	BP_TORSOCAP_LEFTLEG3 = 209

	# Torso Cap | Right Leg
	BP_TORSOCAP_RIGHTLEG = 210

	# Torso Cap | Right Leg 2
	BP_TORSOCAP_RIGHTLEG2 = 211

	# Torso Cap | Right Leg 3
	BP_TORSOCAP_RIGHTLEG3 = 212

	# Torso Cap | Brain
	BP_TORSOCAP_BRAIN = 213

	# Skyrim, Head slot, use for neck on character head
	SBP_230_HEAD = 230

	# Torso Section | Head
	BP_TORSOSECTION_HEAD = 1000

	# Torso Section | Head 2
	BP_TORSOSECTION_HEAD2 = 2000

	# Torso Section | Left Arm
	BP_TORSOSECTION_LEFTARM = 3000

	# Torso Section | Left Arm 2
	BP_TORSOSECTION_LEFTARM2 = 4000

	# Torso Section | Right Arm
	BP_TORSOSECTION_RIGHTARM = 5000

	# Torso Section | Right Arm 2
	BP_TORSOSECTION_RIGHTARM2 = 6000

	# Torso Section | Left Leg
	BP_TORSOSECTION_LEFTLEG = 7000

	# Torso Section | Left Leg 2
	BP_TORSOSECTION_LEFTLEG2 = 8000

	# Torso Section | Left Leg 3
	BP_TORSOSECTION_LEFTLEG3 = 9000

	# Torso Section | Right Leg
	BP_TORSOSECTION_RIGHTLEG = 10000

	# Torso Section | Right Leg 2
	BP_TORSOSECTION_RIGHTLEG2 = 11000

	# Torso Section | Right Leg 3
	BP_TORSOSECTION_RIGHTLEG3 = 12000

	# Torso Section | Brain
	BP_TORSOSECTION_BRAIN = 13000

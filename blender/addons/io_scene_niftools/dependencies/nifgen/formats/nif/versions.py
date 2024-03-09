def version_from_str(version_str):
	"""Converts version string into an integer.

	:param version_str: The version string.
	:type version_str: str
	:return: A version integer.

	>>> hex(NifFormat.version_number('3.14.15.29'))
	'0x30e0f1d'
	>>> hex(NifFormat.version_number('1.2'))
	'0x1020000'
	>>> hex(NifFormat.version_number('3.03'))
	'0x3000300'
	>>> hex(NifFormat.version_number('NS'))
	'0xa010000'
	"""

	# 3.03 case is special
	if version_str == '3.03':
		return 0x03000300

	# NS (neosteam) case is special
	if version_str == 'NS':
		return 0x0A010000

	try:
		ver_list = [int(x) for x in version_str.split('.')]
	except ValueError:
		return -1 # version not supported (i.e. version_str '10.0.1.3a' would trigger this)
	if len(ver_list) > 4 or len(ver_list) < 1:
		return -1 # version not supported
	for ver_digit in ver_list:
		if (ver_digit | 0xff) > 0xff:
			return -1 # version not supported
	while len(ver_list) < 4: ver_list.append(0)
	return (ver_list[0] << 24) + (ver_list[1] << 16) + (ver_list[2] << 8) + ver_list[3]

def has_bs_ver(version, user_version):
	# condition copied from xml, update if it changes
	if (version == 167772418) or (((version == 335675399) or ((version == 335544325) or ((version >= 167837696) and ((version <= 335544324) and (user_version <= 11))))) and (user_version >= 3)):
		return True
	else:
		return False


from enum import Enum

from nifgen.base_version import VersionBase


def is_v10_0_1_0(context):
	if context.version == 167772416:
		return True


def set_v10_0_1_0(context):
	context.version = 167772416


def is_v10_0_1_2(context):
	if context.version == 167772418 and context.bs_header.bs_version in (1, 3):
		return True


def set_v10_0_1_2(context):
	context.version = 167772418
	context.bs_header.bs_version = 1


def is_v10_1_0_0(context):
	if context.version == 167837696:
		return True


def set_v10_1_0_0(context):
	context.version = 167837696


def is_v10_1_0_101(context):
	if context.version == 167837797 and context.user_version == 10 and context.bs_header.bs_version == 4:
		return True


def set_v10_1_0_101(context):
	context.version = 167837797
	context.user_version = 10
	context.bs_header.bs_version = 4


def is_v10_1_0_106(context):
	if context.version == 167837802 and context.user_version == 10 and context.bs_header.bs_version == 5:
		return True


def set_v10_1_0_106(context):
	context.version = 167837802
	context.user_version = 10
	context.bs_header.bs_version = 5


def is_v10_2_0_0(context):
	if context.version == 167903232 and context.user_version == 0:
		return True


def set_v10_2_0_0(context):
	context.version = 167903232
	context.user_version = 0


def is_v10_2_0_0__1(context):
	if context.version == 167903232 and context.user_version == 1:
		return True


def set_v10_2_0_0__1(context):
	context.version = 167903232
	context.user_version = 1


def is_v10_2_0_0__10(context):
	if context.version == 167903232 and context.user_version == 10 and context.bs_header.bs_version in (6, 7, 8, 9, 11):
		return True


def set_v10_2_0_0__10(context):
	context.version = 167903232
	context.user_version = 10
	context.bs_header.bs_version = 6


def is_v10_2_0_1(context):
	if context.version == 167903233:
		return True


def set_v10_2_0_1(context):
	context.version = 167903233


def is_v10_3_0_1(context):
	if context.version == 167968769:
		return True


def set_v10_3_0_1(context):
	context.version = 167968769


def is_v10_4_0_1(context):
	if context.version == 168034305:
		return True


def set_v10_4_0_1(context):
	context.version = 168034305


def is_v20_0_0_4(context):
	if context.version == 335544324 and context.user_version == 0:
		return True


def set_v20_0_0_4(context):
	context.version = 335544324
	context.user_version = 0


def is_v20_0_0_4__10(context):
	if context.version == 335544324 and context.user_version == 10 and context.bs_header.bs_version == 11:
		return True


def set_v20_0_0_4__10(context):
	context.version = 335544324
	context.user_version = 10
	context.bs_header.bs_version = 11


def is_v20_0_0_4__11(context):
	if context.version == 335544324 and context.user_version == 11 and context.bs_header.bs_version == 11:
		return True


def set_v20_0_0_4__11(context):
	context.version = 335544324
	context.user_version = 11
	context.bs_header.bs_version = 11


def is_v20_0_0_5_obl(context):
	if context.version == 335544325 and context.user_version in (10, 11) and context.bs_header.bs_version == 11:
		return True


def set_v20_0_0_5_obl(context):
	context.version = 335544325
	context.user_version = 10
	context.bs_header.bs_version = 11


def is_v20_1_0_3(context):
	if context.version == 335609859:
		return True


def set_v20_1_0_3(context):
	context.version = 335609859


def is_v20_2_0_7(context):
	if context.version == 335675399 and context.user_version == 0:
		return True


def set_v20_2_0_7(context):
	context.version = 335675399
	context.user_version = 0


def is_v20_2_0_7_f76(context):
	if context.version == 335675399 and context.user_version == 12 and context.bs_header.bs_version == 155:
		return True


def set_v20_2_0_7_f76(context):
	context.version = 335675399
	context.user_version = 12
	context.bs_header.bs_version = 155


def is_v20_2_0_7_fo3(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version == 34:
		return True


def set_v20_2_0_7_fo3(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 34


def is_v20_2_0_7_fo4(context):
	if context.version == 335675399 and context.user_version == 12 and context.bs_header.bs_version == 130:
		return True


def set_v20_2_0_7_fo4(context):
	context.version = 335675399
	context.user_version = 12
	context.bs_header.bs_version = 130


def is_v20_2_0_7_fo4_2(context):
	if context.version == 335675399 and context.user_version == 12 and context.bs_header.bs_version in (132, 139):
		return True


def set_v20_2_0_7_fo4_2(context):
	context.version = 335675399
	context.user_version = 12
	context.bs_header.bs_version = 132


def is_v20_2_0_7_sky(context):
	if context.version == 335675399 and context.user_version == 12 and context.bs_header.bs_version == 83:
		return True


def set_v20_2_0_7_sky(context):
	context.version = 335675399
	context.user_version = 12
	context.bs_header.bs_version = 83


def is_v20_2_0_7_sse(context):
	if context.version == 335675399 and context.user_version == 12 and context.bs_header.bs_version == 100:
		return True


def set_v20_2_0_7_sse(context):
	context.version = 335675399
	context.user_version = 12
	context.bs_header.bs_version = 100


def is_v20_2_0_7__11_1(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version == 14:
		return True


def set_v20_2_0_7__11_1(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 14


def is_v20_2_0_7__11_2(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version == 16:
		return True


def set_v20_2_0_7__11_2(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 16


def is_v20_2_0_7__11_3(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version == 21:
		return True


def set_v20_2_0_7__11_3(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 21


def is_v20_2_0_7__11_4(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version == 24:
		return True


def set_v20_2_0_7__11_4(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 24


def is_v20_2_0_7__11_5(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version == 25:
		return True


def set_v20_2_0_7__11_5(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 25


def is_v20_2_0_7__11_6(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version == 26:
		return True


def set_v20_2_0_7__11_6(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 26


def is_v20_2_0_7__11_7(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version in (27, 28):
		return True


def set_v20_2_0_7__11_7(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 27


def is_v20_2_0_7__11_8(context):
	if context.version == 335675399 and context.user_version == 11 and context.bs_header.bs_version in (30, 31, 32, 33):
		return True


def set_v20_2_0_7__11_8(context):
	context.version = 335675399
	context.user_version = 11
	context.bs_header.bs_version = 30


def is_v20_2_0_8(context):
	if context.version == 335675400:
		return True


def set_v20_2_0_8(context):
	context.version = 335675400


def is_v20_2_4_7(context):
	if context.version == 335676695:
		return True


def set_v20_2_4_7(context):
	context.version = 335676695


def is_v20_3_0_1(context):
	if context.version == 335740929:
		return True


def set_v20_3_0_1(context):
	context.version = 335740929


def is_v20_3_0_2(context):
	if context.version == 335740930:
		return True


def set_v20_3_0_2(context):
	context.version = 335740930


def is_v20_3_0_3(context):
	if context.version == 335740931:
		return True


def set_v20_3_0_3(context):
	context.version = 335740931


def is_v20_3_0_6(context):
	if context.version == 335740934:
		return True


def set_v20_3_0_6(context):
	context.version = 335740934


def is_v20_3_0_9(context):
	if context.version == 335740937 and context.user_version in (0, 65536):
		return True


def set_v20_3_0_9(context):
	context.version = 335740937
	context.user_version = 0


def is_v20_3_0_9_div2(context):
	if context.version == 335740937 and context.user_version in (131072, 196608):
		return True


def set_v20_3_0_9_div2(context):
	context.version = 335740937
	context.user_version = 131072


def is_v20_3_1_1(context):
	if context.version == 335741185:
		return True


def set_v20_3_1_1(context):
	context.version = 335741185


def is_v20_3_1_2(context):
	if context.version == 335741186:
		return True


def set_v20_3_1_2(context):
	context.version = 335741186


def is_v20_5_0_0(context):
	if context.version == 335872000:
		return True


def set_v20_5_0_0(context):
	context.version = 335872000


def is_v20_6_0_0(context):
	if context.version == 335937536:
		return True


def set_v20_6_0_0(context):
	context.version = 335937536


def is_v20_6_0_2(context):
	if context.version == 335937538:
		return True


def set_v20_6_0_2(context):
	context.version = 335937538


def is_v20_6_5_0(context):
	if context.version == 335938816 and context.user_version == 0:
		return True


def set_v20_6_5_0(context):
	context.version = 335938816
	context.user_version = 0


def is_v20_6_5_0_dem(context):
	if context.version == 335938816 and context.user_version in (14, 15):
		return True


def set_v20_6_5_0_dem(context):
	context.version = 335938816
	context.user_version = 14


def is_v20_6_5_0_dem2(context):
	if context.version == 335938816 and context.user_version == 17:
		return True


def set_v20_6_5_0_dem2(context):
	context.version = 335938816
	context.user_version = 17


def is_v2_3(context):
	if context.version == 33751040:
		return True


def set_v2_3(context):
	context.version = 33751040


def is_v30_0_0_2(context):
	if context.version == 503316482:
		return True


def set_v30_0_0_2(context):
	context.version = 503316482


def is_v30_1_0_1(context):
	if context.version == 503382017:
		return True


def set_v30_1_0_1(context):
	context.version = 503382017


def is_v30_1_0_3(context):
	if context.version == 503382019:
		return True


def set_v30_1_0_3(context):
	context.version = 503382019


def is_v30_2_0_3(context):
	if context.version == 503447555:
		return True


def set_v30_2_0_3(context):
	context.version = 503447555


def is_v3_0(context):
	if context.version == 50331648:
		return True


def set_v3_0(context):
	context.version = 50331648


def is_v3_03(context):
	if context.version == 50528256:
		return True


def set_v3_03(context):
	context.version = 50528256


def is_v3_1(context):
	if context.version == 50397184:
		return True


def set_v3_1(context):
	context.version = 50397184


def is_v3_3_0_13(context):
	if context.version == 50528269:
		return True


def set_v3_3_0_13(context):
	context.version = 50528269


def is_v4_0_0_0(context):
	if context.version == 67108864:
		return True


def set_v4_0_0_0(context):
	context.version = 67108864


def is_v4_0_0_2(context):
	if context.version == 67108866:
		return True


def set_v4_0_0_2(context):
	context.version = 67108866


def is_v4_1_0_12(context):
	if context.version == 67174412:
		return True


def set_v4_1_0_12(context):
	context.version = 67174412


def is_v4_2_0_2(context):
	if context.version == 67239938:
		return True


def set_v4_2_0_2(context):
	context.version = 67239938


def is_v4_2_1_0(context):
	if context.version == 67240192:
		return True


def set_v4_2_1_0(context):
	context.version = 67240192


def is_v4_2_2_0(context):
	if context.version == 67240448:
		return True


def set_v4_2_2_0(context):
	context.version = 67240448


games = Enum('Games', [('ARCHLORD_2', 'Archlord 2'), ('ATLANTICA_ONLINE', 'Atlantica Online'), ('AURA_KINGDOM', 'Aura Kingdom'), ('AXIS_AND_ALLIES', 'Axis and Allies'), ('BLOOD_BOWL', 'Blood Bowl'), ('BULLY_SE', 'Bully SE'), ('CIVILIZATION_IV', 'Civilization IV'), ('CULPA_INNATA', 'Culpa Innata'), ('DARK_AGE_OF_CAMELOT', 'Dark Age of Camelot'), ('DIGIMON_MASTERS_ONLINE', 'Digimon Masters Online'), ('DIVINITY_2', 'Divinity 2'), ('DIVINITY_2_0_X_10000', 'Divinity 2 (0x10000)'), ('EMERGE', 'Emerge'), ('EMPIRE_EARTH_II', 'Empire Earth II'), ('EMPIRE_EARTH_III', 'Empire Earth III'), ('EPIC_MICKEY', 'Epic Mickey'), ('EPIC_MICKEY_2', 'Epic Mickey 2'), ('FALLOUT_3', 'Fallout 3'), ('FALLOUT_4', 'Fallout 4'), ('FALLOUT_4_LS_MIRELURK_NIF_SCREEN_NIF', 'Fallout 4 (LS_Mirelurk.nif, Screen.nif)'), ('FALLOUT_76', 'Fallout 76'), ('FALLOUT_NV', 'Fallout NV'), ('FANTASY_FRONTIER', 'Fantasy Frontier'), ('FFT_ONLINE', 'FFT Online'), ('FLORENSIA', 'Florensia'), ('FREEDOM_FORCE', 'Freedom Force'), ('FREEDOM_FORCE_VS_THE_3_RD_REICH', 'Freedom Force vs. the 3rd Reich'), ('GHOST_IN_THE_SHELL_FIRST_ASSAULT', 'Ghost In The Shell: First Assault'), ('HOWLING_SWORD', 'Howling Sword'), ('IRIS_ONLINE', 'IRIS Online'), ('KOHAN_2', 'Kohan 2'), ('KRAZY_RAIN', 'KrazyRain'), ('LAZESKA', 'Lazeska'), ('LEGO_UNIVERSE', 'LEGO Universe'), ('LOKI', 'Loki'), ('MAPLE_STORY_2', 'MapleStory 2'), ('MICRO_VOLTS', 'MicroVolts'), ('MORROWIND', 'Morrowind'), ('MUNCH_S_ODDYSEE', "Munch's Oddysee"), ('MXM', 'MXM'), ('NEO_STEAM', 'NeoSteam'), ('OBLIVION', 'Oblivion'), ('OBLIVION_KF', 'Oblivion KF'), ('PRISON_TYCOON', 'Prison Tycoon'), ('PRO_CYCLING_MANAGER', 'Pro Cycling Manager'), ('Q_Q_SPEED', 'QQSpeed'), ('RAGNAROK_ONLINE_2', 'Ragnarok Online 2'), ('RED_OCEAN', 'Red Ocean'), ('ROCKSMITH', 'Rocksmith'), ('ROCKSMITH_2014', 'Rocksmith 2014'), ('SHIN_MEGAMI_TENSEI_IMAGINE', 'Shin Megami Tensei: Imagine'), ('SID_MEIER_S_PIRATES', "Sid Meier's Pirates!"), ('SID_MEIER_S_RAILROADS', "Sid Meier's Railroads"), ('SKYRIM', 'Skyrim'), ('SKYRIM_SE', 'Skyrim SE'), ('STAR_TREK_BRIDGE_COMMANDER', 'Star Trek: Bridge Commander'), ('THE_GUILD_2', 'The Guild 2'), ('WARHAMMER', 'Warhammer'), ('WILDLIFE_PARK_2', 'Wildlife Park 2'), ('WIZARD_101', 'Wizard101'), ('WORLD_SHIFT', 'WorldShift'), ('ZOO_TYCOON_2', 'Zoo Tycoon 2'), ('UNKNOWN', 'Unknown Game')])


def get_game(context):
	if is_v10_0_1_0(context):
		return [games.ZOO_TYCOON_2, games.CIVILIZATION_IV, games.OBLIVION]
	if is_v10_0_1_2(context):
		return [games.OBLIVION]
	if is_v10_1_0_0(context):
		return [games.FREEDOM_FORCE_VS_THE_3_RD_REICH, games.AXIS_AND_ALLIES, games.EMPIRE_EARTH_II, games.KOHAN_2, games.SID_MEIER_S_PIRATES, games.DARK_AGE_OF_CAMELOT, games.CIVILIZATION_IV, games.WILDLIFE_PARK_2, games.THE_GUILD_2, games.NEO_STEAM]
	if is_v10_1_0_101(context):
		return [games.OBLIVION]
	if is_v10_1_0_106(context):
		return [games.OBLIVION]
	if is_v10_2_0_0(context):
		return [games.PRO_CYCLING_MANAGER, games.PRISON_TYCOON, games.RED_OCEAN, games.WILDLIFE_PARK_2, games.CIVILIZATION_IV, games.LOKI]
	if is_v10_2_0_0__1(context):
		return [games.BLOOD_BOWL]
	if is_v10_2_0_0__10(context):
		return [games.OBLIVION]
	if is_v10_2_0_1(context):
		return [games.WORLD_SHIFT]
	if is_v10_3_0_1(context):
		return [games.WORLD_SHIFT]
	if is_v10_4_0_1(context):
		return [games.WORLD_SHIFT]
	if is_v20_0_0_4(context):
		return [games.CIVILIZATION_IV, games.SID_MEIER_S_RAILROADS, games.FLORENSIA, games.RAGNAROK_ONLINE_2, games.IRIS_ONLINE]
	if is_v20_0_0_4__10(context):
		return [games.OBLIVION_KF, games.OBLIVION]
	if is_v20_0_0_4__11(context):
		return [games.OBLIVION, games.FALLOUT_3]
	if is_v20_0_0_5_obl(context):
		return [games.OBLIVION]
	if is_v20_1_0_3(context):
		return [games.SHIN_MEGAMI_TENSEI_IMAGINE]
	if is_v20_2_0_7(context):
		return [games.FLORENSIA, games.EMPIRE_EARTH_III, games.ATLANTICA_ONLINE, games.IRIS_ONLINE, games.WIZARD_101]
	if is_v20_2_0_7_f76(context):
		return [games.FALLOUT_76]
	if is_v20_2_0_7_fo3(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_7_fo4(context):
		return [games.FALLOUT_4]
	if is_v20_2_0_7_fo4_2(context):
		return [games.FALLOUT_4_LS_MIRELURK_NIF_SCREEN_NIF]
	if is_v20_2_0_7_sky(context):
		return [games.SKYRIM]
	if is_v20_2_0_7_sse(context):
		return [games.SKYRIM_SE]
	if is_v20_2_0_7__11_1(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_7__11_2(context):
		return [games.FALLOUT_3]
	if is_v20_2_0_7__11_3(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_7__11_4(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_7__11_5(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_7__11_6(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_7__11_7(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_7__11_8(context):
		return [games.FALLOUT_3, games.FALLOUT_NV]
	if is_v20_2_0_8(context):
		return [games.EMPIRE_EARTH_III, games.FFT_ONLINE, games.ATLANTICA_ONLINE, games.IRIS_ONLINE, games.WIZARD_101]
	if is_v20_2_4_7(context):
		return [games.Q_Q_SPEED]
	if is_v20_3_0_1(context):
		return [games.EMERGE]
	if is_v20_3_0_2(context):
		return [games.EMERGE]
	if is_v20_3_0_3(context):
		return [games.EMERGE]
	if is_v20_3_0_6(context):
		return [games.EMERGE]
	if is_v20_3_0_9(context):
		return [games.BULLY_SE, games.LEGO_UNIVERSE, games.WARHAMMER, games.LAZESKA, games.HOWLING_SWORD, games.RAGNAROK_ONLINE_2, games.DIVINITY_2_0_X_10000, games.DIGIMON_MASTERS_ONLINE]
	if is_v20_3_0_9_div2(context):
		return [games.DIVINITY_2]
	if is_v20_3_1_1(context):
		return [games.FANTASY_FRONTIER, games.AURA_KINGDOM]
	if is_v20_3_1_2(context):
		return [games.FANTASY_FRONTIER, games.AURA_KINGDOM]
	if is_v20_5_0_0(context):
		return [games.MICRO_VOLTS, games.KRAZY_RAIN]
	if is_v20_6_0_0(context):
		return [games.MICRO_VOLTS, games.IRIS_ONLINE, games.RAGNAROK_ONLINE_2, games.KRAZY_RAIN, games.ATLANTICA_ONLINE, games.WIZARD_101, games.ARCHLORD_2]
	if is_v20_6_0_2(context):
		return [games.MXM]
	if is_v20_6_5_0(context):
		return [games.EPIC_MICKEY]
	if is_v20_6_5_0_dem(context):
		return [games.EPIC_MICKEY]
	if is_v20_6_5_0_dem2(context):
		return [games.EPIC_MICKEY_2]
	if is_v2_3(context):
		return [games.DARK_AGE_OF_CAMELOT]
	if is_v30_0_0_2(context):
		return [games.EMERGE]
	if is_v30_1_0_1(context):
		return [games.EMERGE]
	if is_v30_1_0_3(context):
		return [games.ROCKSMITH, games.ROCKSMITH_2014]
	if is_v30_2_0_3(context):
		return [games.GHOST_IN_THE_SHELL_FIRST_ASSAULT, games.MAPLE_STORY_2]
	if is_v3_0(context):
		return [games.STAR_TREK_BRIDGE_COMMANDER]
	if is_v3_03(context):
		return [games.DARK_AGE_OF_CAMELOT]
	if is_v3_1(context):
		return [games.DARK_AGE_OF_CAMELOT, games.STAR_TREK_BRIDGE_COMMANDER]
	if is_v3_3_0_13(context):
		return [games.MUNCH_S_ODDYSEE, games.OBLIVION]
	if is_v4_0_0_0(context):
		return [games.FREEDOM_FORCE]
	if is_v4_0_0_2(context):
		return [games.MORROWIND, games.FREEDOM_FORCE]
	if is_v4_1_0_12(context):
		return [games.DARK_AGE_OF_CAMELOT]
	if is_v4_2_0_2(context):
		return [games.CIVILIZATION_IV]
	if is_v4_2_1_0(context):
		return [games.DARK_AGE_OF_CAMELOT, games.CIVILIZATION_IV]
	if is_v4_2_2_0(context):
		return [games.CULPA_INNATA, games.CIVILIZATION_IV, games.DARK_AGE_OF_CAMELOT, games.EMPIRE_EARTH_II]
	return [games.UNKNOWN]


def set_game(context, game):
	if isinstance(game, str):
		game = games(game)
	if game in {games.ZOO_TYCOON_2}:
		return set_v10_0_1_0(context)
	if game in {games.SID_MEIER_S_PIRATES, games.EMPIRE_EARTH_II, games.AXIS_AND_ALLIES, games.KOHAN_2, games.FREEDOM_FORCE_VS_THE_3_RD_REICH}:
		return set_v10_1_0_0(context)
	if game in {games.PRO_CYCLING_MANAGER, games.RED_OCEAN, games.WILDLIFE_PARK_2, games.PRISON_TYCOON}:
		return set_v10_2_0_0(context)
	if game in {games.BLOOD_BOWL}:
		return set_v10_2_0_0__1(context)
	if game in {games.WORLD_SHIFT}:
		return set_v10_4_0_1(context)
	if game in {games.CIVILIZATION_IV, games.SID_MEIER_S_RAILROADS}:
		return set_v20_0_0_4(context)
	if game in {games.OBLIVION_KF}:
		return set_v20_0_0_4__10(context)
	if game in {games.OBLIVION}:
		return set_v20_0_0_5_obl(context)
	if game in {games.SHIN_MEGAMI_TENSEI_IMAGINE}:
		return set_v20_1_0_3(context)
	if game in {games.FLORENSIA}:
		return set_v20_2_0_7(context)
	if game in {games.FALLOUT_76}:
		return set_v20_2_0_7_f76(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7_fo3(context)
	if game in {games.FALLOUT_4}:
		return set_v20_2_0_7_fo4(context)
	if game in {games.SKYRIM}:
		return set_v20_2_0_7_sky(context)
	if game in {games.SKYRIM_SE}:
		return set_v20_2_0_7_sse(context)
	if game in {games.FFT_ONLINE, games.EMPIRE_EARTH_III}:
		return set_v20_2_0_8(context)
	if game in {games.LEGO_UNIVERSE, games.BULLY_SE}:
		return set_v20_3_0_9(context)
	if game in {games.DIVINITY_2}:
		return set_v20_3_0_9_div2(context)
	if game in {games.FANTASY_FRONTIER, games.AURA_KINGDOM}:
		return set_v20_3_1_2(context)
	if game in {games.IRIS_ONLINE, games.MICRO_VOLTS, games.RAGNAROK_ONLINE_2}:
		return set_v20_6_0_0(context)
	if game in {games.MXM}:
		return set_v20_6_0_2(context)
	if game in {games.MUNCH_S_ODDYSEE}:
		return set_v3_3_0_13(context)
	if game in {games.FREEDOM_FORCE, games.MORROWIND}:
		return set_v4_0_0_2(context)
	if game in {games.CULPA_INNATA}:
		return set_v4_2_2_0(context)
	if game in {games.OBLIVION, games.CIVILIZATION_IV}:
		return set_v10_0_1_0(context)
	if game in {games.OBLIVION}:
		return set_v10_0_1_2(context)
	if game in {games.CIVILIZATION_IV, games.DARK_AGE_OF_CAMELOT, games.THE_GUILD_2, games.WILDLIFE_PARK_2, games.NEO_STEAM}:
		return set_v10_1_0_0(context)
	if game in {games.OBLIVION}:
		return set_v10_1_0_101(context)
	if game in {games.OBLIVION}:
		return set_v10_1_0_106(context)
	if game in {games.LOKI, games.CIVILIZATION_IV}:
		return set_v10_2_0_0(context)
	if game in {games.OBLIVION}:
		return set_v10_2_0_0__10(context)
	if game in {games.WORLD_SHIFT}:
		return set_v10_2_0_1(context)
	if game in {games.WORLD_SHIFT}:
		return set_v10_3_0_1(context)
	if game in {games.IRIS_ONLINE, games.RAGNAROK_ONLINE_2, games.FLORENSIA}:
		return set_v20_0_0_4(context)
	if game in {games.OBLIVION}:
		return set_v20_0_0_4__10(context)
	if game in {games.OBLIVION, games.FALLOUT_3}:
		return set_v20_0_0_4__11(context)
	if game in {games.IRIS_ONLINE, games.EMPIRE_EARTH_III, games.WIZARD_101, games.ATLANTICA_ONLINE}:
		return set_v20_2_0_7(context)
	if game in {games.FALLOUT_4_LS_MIRELURK_NIF_SCREEN_NIF}:
		return set_v20_2_0_7_fo4_2(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7__11_1(context)
	if game in {games.FALLOUT_3}:
		return set_v20_2_0_7__11_2(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7__11_3(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7__11_4(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7__11_5(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7__11_6(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7__11_7(context)
	if game in {games.FALLOUT_NV, games.FALLOUT_3}:
		return set_v20_2_0_7__11_8(context)
	if game in {games.IRIS_ONLINE, games.WIZARD_101, games.ATLANTICA_ONLINE}:
		return set_v20_2_0_8(context)
	if game in {games.Q_Q_SPEED}:
		return set_v20_2_4_7(context)
	if game in {games.EMERGE}:
		return set_v20_3_0_1(context)
	if game in {games.EMERGE}:
		return set_v20_3_0_2(context)
	if game in {games.EMERGE}:
		return set_v20_3_0_3(context)
	if game in {games.EMERGE}:
		return set_v20_3_0_6(context)
	if game in {games.DIGIMON_MASTERS_ONLINE, games.RAGNAROK_ONLINE_2, games.HOWLING_SWORD, games.WARHAMMER, games.DIVINITY_2_0_X_10000, games.LAZESKA}:
		return set_v20_3_0_9(context)
	if game in {games.FANTASY_FRONTIER, games.AURA_KINGDOM}:
		return set_v20_3_1_1(context)
	if game in {games.MICRO_VOLTS, games.KRAZY_RAIN}:
		return set_v20_5_0_0(context)
	if game in {games.ARCHLORD_2, games.WIZARD_101, games.ATLANTICA_ONLINE, games.KRAZY_RAIN}:
		return set_v20_6_0_0(context)
	if game in {games.EPIC_MICKEY}:
		return set_v20_6_5_0(context)
	if game in {games.EPIC_MICKEY}:
		return set_v20_6_5_0_dem(context)
	if game in {games.EPIC_MICKEY_2}:
		return set_v20_6_5_0_dem2(context)
	if game in {games.DARK_AGE_OF_CAMELOT}:
		return set_v2_3(context)
	if game in {games.EMERGE}:
		return set_v30_0_0_2(context)
	if game in {games.EMERGE}:
		return set_v30_1_0_1(context)
	if game in {games.ROCKSMITH_2014, games.ROCKSMITH}:
		return set_v30_1_0_3(context)
	if game in {games.GHOST_IN_THE_SHELL_FIRST_ASSAULT, games.MAPLE_STORY_2}:
		return set_v30_2_0_3(context)
	if game in {games.STAR_TREK_BRIDGE_COMMANDER}:
		return set_v3_0(context)
	if game in {games.DARK_AGE_OF_CAMELOT}:
		return set_v3_03(context)
	if game in {games.DARK_AGE_OF_CAMELOT, games.STAR_TREK_BRIDGE_COMMANDER}:
		return set_v3_1(context)
	if game in {games.OBLIVION}:
		return set_v3_3_0_13(context)
	if game in {games.FREEDOM_FORCE}:
		return set_v4_0_0_0(context)
	if game in {games.DARK_AGE_OF_CAMELOT}:
		return set_v4_1_0_12(context)
	if game in {games.CIVILIZATION_IV}:
		return set_v4_2_0_2(context)
	if game in {games.DARK_AGE_OF_CAMELOT, games.CIVILIZATION_IV}:
		return set_v4_2_1_0(context)
	if game in {games.DARK_AGE_OF_CAMELOT, games.CIVILIZATION_IV, games.EMPIRE_EARTH_II}:
		return set_v4_2_2_0(context)


class NifVersion(VersionBase):

	_file_format = 'nif'
	_verattrs = ('num', 'user', 'bsver')

	def __init__(self, *args, num=(), user=(), bsver=(), **kwargs):
		super().__init__(*args, **kwargs)
		self.num = self._force_tuple(num)
		self.user = self._force_tuple(user)
		self.bsver = self._force_tuple(bsver)


v10_0_1_0 = NifVersion(id='V10_0_1_0', num=(167772416,), primary_games=[games.ZOO_TYCOON_2], all_games=[games.ZOO_TYCOON_2, games.CIVILIZATION_IV, games.OBLIVION])
v10_0_1_2 = NifVersion(id='V10_0_1_2', num=(167772418,), bsver=(1, 3,), primary_games=[], all_games=[games.OBLIVION])
v10_1_0_0 = NifVersion(id='V10_1_0_0', num=(167837696,), primary_games=[games.FREEDOM_FORCE_VS_THE_3_RD_REICH, games.AXIS_AND_ALLIES, games.EMPIRE_EARTH_II, games.KOHAN_2, games.SID_MEIER_S_PIRATES], all_games=[games.FREEDOM_FORCE_VS_THE_3_RD_REICH, games.AXIS_AND_ALLIES, games.EMPIRE_EARTH_II, games.KOHAN_2, games.SID_MEIER_S_PIRATES, games.DARK_AGE_OF_CAMELOT, games.CIVILIZATION_IV, games.WILDLIFE_PARK_2, games.THE_GUILD_2, games.NEO_STEAM])
v10_1_0_101 = NifVersion(id='V10_1_0_101', num=(167837797,), user=(10,), bsver=(4,), primary_games=[], all_games=[games.OBLIVION])
v10_1_0_106 = NifVersion(id='V10_1_0_106', num=(167837802,), user=(10,), bsver=(5,), primary_games=[], all_games=[games.OBLIVION])
v10_2_0_0 = NifVersion(id='V10_2_0_0', num=(167903232,), user=(0,), primary_games=[games.PRO_CYCLING_MANAGER, games.PRISON_TYCOON, games.RED_OCEAN, games.WILDLIFE_PARK_2], all_games=[games.PRO_CYCLING_MANAGER, games.PRISON_TYCOON, games.RED_OCEAN, games.WILDLIFE_PARK_2, games.CIVILIZATION_IV, games.LOKI])
v10_2_0_0__1 = NifVersion(id='V10_2_0_0__1', num=(167903232,), user=(1,), primary_games=[games.BLOOD_BOWL], all_games=[games.BLOOD_BOWL])
v10_2_0_0__10 = NifVersion(id='V10_2_0_0__10', num=(167903232,), user=(10,), bsver=(6, 7, 8, 9, 11,), primary_games=[], all_games=[games.OBLIVION])
v10_2_0_1 = NifVersion(id='V10_2_0_1', num=(167903233,), custom=True, primary_games=[], all_games=[games.WORLD_SHIFT])
v10_3_0_1 = NifVersion(id='V10_3_0_1', num=(167968769,), custom=True, primary_games=[], all_games=[games.WORLD_SHIFT])
v10_4_0_1 = NifVersion(id='V10_4_0_1', num=(168034305,), custom=True, primary_games=[games.WORLD_SHIFT], all_games=[games.WORLD_SHIFT])
v20_0_0_4 = NifVersion(id='V20_0_0_4', num=(335544324,), user=(0,), primary_games=[games.CIVILIZATION_IV, games.SID_MEIER_S_RAILROADS], all_games=[games.CIVILIZATION_IV, games.SID_MEIER_S_RAILROADS, games.FLORENSIA, games.RAGNAROK_ONLINE_2, games.IRIS_ONLINE])
v20_0_0_4__10 = NifVersion(id='V20_0_0_4__10', num=(335544324,), user=(10,), bsver=(11,), primary_games=[games.OBLIVION_KF], all_games=[games.OBLIVION_KF, games.OBLIVION])
v20_0_0_4__11 = NifVersion(id='V20_0_0_4__11', num=(335544324,), user=(11,), bsver=(11,), primary_games=[], all_games=[games.OBLIVION, games.FALLOUT_3])
v20_0_0_5_obl = NifVersion(id='V20_0_0_5_OBL', num=(335544325,), user=(10, 11,), bsver=(11,), primary_games=[games.OBLIVION], all_games=[games.OBLIVION])
v20_1_0_3 = NifVersion(id='V20_1_0_3', num=(335609859,), primary_games=[games.SHIN_MEGAMI_TENSEI_IMAGINE], all_games=[games.SHIN_MEGAMI_TENSEI_IMAGINE])
v20_2_0_7 = NifVersion(id='V20_2_0_7', num=(335675399,), user=(0,), primary_games=[games.FLORENSIA], all_games=[games.FLORENSIA, games.EMPIRE_EARTH_III, games.ATLANTICA_ONLINE, games.IRIS_ONLINE, games.WIZARD_101])
v20_2_0_7_f76 = NifVersion(id='V20_2_0_7_F76', num=(335675399,), user=(12,), bsver=(155,), ext=('bto',), primary_games=[games.FALLOUT_76], all_games=[games.FALLOUT_76])
v20_2_0_7_fo3 = NifVersion(id='V20_2_0_7_FO3', num=(335675399,), user=(11,), bsver=(34,), ext=('rdt',), primary_games=[games.FALLOUT_3, games.FALLOUT_NV], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_7_fo4 = NifVersion(id='V20_2_0_7_FO4', num=(335675399,), user=(12,), bsver=(130,), ext=('bto', 'btr',), primary_games=[games.FALLOUT_4], all_games=[games.FALLOUT_4])
v20_2_0_7_fo4_2 = NifVersion(id='V20_2_0_7_FO4_2', num=(335675399,), user=(12,), bsver=(132, 139,), supported=False, ext=('bto', 'btr',), primary_games=[], all_games=[games.FALLOUT_4_LS_MIRELURK_NIF_SCREEN_NIF])
v20_2_0_7_sky = NifVersion(id='V20_2_0_7_SKY', num=(335675399,), user=(12,), bsver=(83,), ext=('bto', 'btr',), primary_games=[games.SKYRIM], all_games=[games.SKYRIM])
v20_2_0_7_sse = NifVersion(id='V20_2_0_7_SSE', num=(335675399,), user=(12,), bsver=(100,), ext=('bto', 'btr',), primary_games=[games.SKYRIM_SE], all_games=[games.SKYRIM_SE])
v20_2_0_7__11_1 = NifVersion(id='V20_2_0_7__11_1', num=(335675399,), user=(11,), bsver=(14,), primary_games=[], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_7__11_2 = NifVersion(id='V20_2_0_7__11_2', num=(335675399,), user=(11,), bsver=(16,), ext=('rdt',), primary_games=[], all_games=[games.FALLOUT_3])
v20_2_0_7__11_3 = NifVersion(id='V20_2_0_7__11_3', num=(335675399,), user=(11,), bsver=(21,), primary_games=[], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_7__11_4 = NifVersion(id='V20_2_0_7__11_4', num=(335675399,), user=(11,), bsver=(24,), primary_games=[], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_7__11_5 = NifVersion(id='V20_2_0_7__11_5', num=(335675399,), user=(11,), bsver=(25,), primary_games=[], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_7__11_6 = NifVersion(id='V20_2_0_7__11_6', num=(335675399,), user=(11,), bsver=(26,), primary_games=[], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_7__11_7 = NifVersion(id='V20_2_0_7__11_7', num=(335675399,), user=(11,), bsver=(27, 28,), primary_games=[], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_7__11_8 = NifVersion(id='V20_2_0_7__11_8', num=(335675399,), user=(11,), bsver=(30, 31, 32, 33,), primary_games=[], all_games=[games.FALLOUT_3, games.FALLOUT_NV])
v20_2_0_8 = NifVersion(id='V20_2_0_8', num=(335675400,), ext=('nifcache',), primary_games=[games.EMPIRE_EARTH_III, games.FFT_ONLINE], all_games=[games.EMPIRE_EARTH_III, games.FFT_ONLINE, games.ATLANTICA_ONLINE, games.IRIS_ONLINE, games.WIZARD_101])
v20_2_4_7 = NifVersion(id='V20_2_4_7', num=(335676695,), primary_games=[], all_games=[games.Q_Q_SPEED])
v20_3_0_1 = NifVersion(id='V20_3_0_1', num=(335740929,), primary_games=[], all_games=[games.EMERGE])
v20_3_0_2 = NifVersion(id='V20_3_0_2', num=(335740930,), primary_games=[], all_games=[games.EMERGE])
v20_3_0_3 = NifVersion(id='V20_3_0_3', num=(335740931,), primary_games=[], all_games=[games.EMERGE])
v20_3_0_6 = NifVersion(id='V20_3_0_6', num=(335740934,), primary_games=[], all_games=[games.EMERGE])
v20_3_0_9 = NifVersion(id='V20_3_0_9', num=(335740937,), user=(0, 65536,), ext=('nft', 'item', 'cat',), primary_games=[games.BULLY_SE, games.LEGO_UNIVERSE], all_games=[games.BULLY_SE, games.LEGO_UNIVERSE, games.WARHAMMER, games.LAZESKA, games.HOWLING_SWORD, games.RAGNAROK_ONLINE_2, games.DIVINITY_2_0_X_10000, games.DIGIMON_MASTERS_ONLINE])
v20_3_0_9_div2 = NifVersion(id='V20_3_0_9_DIV2', num=(335740937,), user=(131072, 196608,), ext=('item', 'cat',), primary_games=[games.DIVINITY_2], all_games=[games.DIVINITY_2])
v20_3_1_1 = NifVersion(id='V20_3_1_1', num=(335741185,), primary_games=[], all_games=[games.FANTASY_FRONTIER, games.AURA_KINGDOM])
v20_3_1_2 = NifVersion(id='V20_3_1_2', num=(335741186,), primary_games=[games.FANTASY_FRONTIER, games.AURA_KINGDOM], all_games=[games.FANTASY_FRONTIER, games.AURA_KINGDOM])
v20_5_0_0 = NifVersion(id='V20_5_0_0', num=(335872000,), primary_games=[], all_games=[games.MICRO_VOLTS, games.KRAZY_RAIN])
v20_6_0_0 = NifVersion(id='V20_6_0_0', num=(335937536,), primary_games=[games.MICRO_VOLTS, games.IRIS_ONLINE, games.RAGNAROK_ONLINE_2], all_games=[games.MICRO_VOLTS, games.IRIS_ONLINE, games.RAGNAROK_ONLINE_2, games.KRAZY_RAIN, games.ATLANTICA_ONLINE, games.WIZARD_101, games.ARCHLORD_2])
v20_6_0_2 = NifVersion(id='V20_6_0_2', num=(335937538,), primary_games=[games.MXM], all_games=[games.MXM])
v20_6_5_0 = NifVersion(id='V20_6_5_0', num=(335938816,), user=(0,), supported=False, primary_games=[], all_games=[games.EPIC_MICKEY])
v20_6_5_0_dem = NifVersion(id='V20_6_5_0_DEM', num=(335938816,), user=(14, 15,), ext=('nif_wii',), primary_games=[], all_games=[games.EPIC_MICKEY])
v20_6_5_0_dem2 = NifVersion(id='V20_6_5_0_DEM2', num=(335938816,), user=(17,), primary_games=[], all_games=[games.EPIC_MICKEY_2])
v2_3 = NifVersion(id='V2_3', num=(33751040,), supported=False, primary_games=[], all_games=[games.DARK_AGE_OF_CAMELOT])
v30_0_0_2 = NifVersion(id='V30_0_0_2', num=(503316482,), primary_games=[], all_games=[games.EMERGE])
v30_1_0_1 = NifVersion(id='V30_1_0_1', num=(503382017,), primary_games=[], all_games=[games.EMERGE])
v30_1_0_3 = NifVersion(id='V30_1_0_3', num=(503382019,), primary_games=[], all_games=[games.ROCKSMITH, games.ROCKSMITH_2014])
v30_2_0_3 = NifVersion(id='V30_2_0_3', num=(503447555,), primary_games=[], all_games=[games.GHOST_IN_THE_SHELL_FIRST_ASSAULT, games.MAPLE_STORY_2])
v3_0 = NifVersion(id='V3_0', num=(50331648,), supported=False, primary_games=[], all_games=[games.STAR_TREK_BRIDGE_COMMANDER])
v3_03 = NifVersion(id='V3_03', num=(50528256,), supported=False, primary_games=[], all_games=[games.DARK_AGE_OF_CAMELOT])
v3_1 = NifVersion(id='V3_1', num=(50397184,), supported=False, primary_games=[], all_games=[games.DARK_AGE_OF_CAMELOT, games.STAR_TREK_BRIDGE_COMMANDER])
v3_3_0_13 = NifVersion(id='V3_3_0_13', num=(50528269,), primary_games=[games.MUNCH_S_ODDYSEE], all_games=[games.MUNCH_S_ODDYSEE, games.OBLIVION])
v4_0_0_0 = NifVersion(id='V4_0_0_0', num=(67108864,), primary_games=[], all_games=[games.FREEDOM_FORCE])
v4_0_0_2 = NifVersion(id='V4_0_0_2', num=(67108866,), primary_games=[games.MORROWIND, games.FREEDOM_FORCE], all_games=[games.MORROWIND, games.FREEDOM_FORCE])
v4_1_0_12 = NifVersion(id='V4_1_0_12', num=(67174412,), primary_games=[], all_games=[games.DARK_AGE_OF_CAMELOT])
v4_2_0_2 = NifVersion(id='V4_2_0_2', num=(67239938,), primary_games=[], all_games=[games.CIVILIZATION_IV])
v4_2_1_0 = NifVersion(id='V4_2_1_0', num=(67240192,), primary_games=[], all_games=[games.DARK_AGE_OF_CAMELOT, games.CIVILIZATION_IV])
v4_2_2_0 = NifVersion(id='V4_2_2_0', num=(67240448,), primary_games=[games.CULPA_INNATA], all_games=[games.CULPA_INNATA, games.CIVILIZATION_IV, games.DARK_AGE_OF_CAMELOT, games.EMPIRE_EARTH_II])

available_versions = [v10_0_1_0, v10_0_1_2, v10_1_0_0, v10_1_0_101, v10_1_0_106, v10_2_0_0, v10_2_0_0__1, v10_2_0_0__10, v10_2_0_1, v10_3_0_1, v10_4_0_1, v20_0_0_4, v20_0_0_4__10, v20_0_0_4__11, v20_0_0_5_obl, v20_1_0_3, v20_2_0_7, v20_2_0_7_f76, v20_2_0_7_fo3, v20_2_0_7_fo4, v20_2_0_7_fo4_2, v20_2_0_7_sky, v20_2_0_7_sse, v20_2_0_7__11_1, v20_2_0_7__11_2, v20_2_0_7__11_3, v20_2_0_7__11_4, v20_2_0_7__11_5, v20_2_0_7__11_6, v20_2_0_7__11_7, v20_2_0_7__11_8, v20_2_0_8, v20_2_4_7, v20_3_0_1, v20_3_0_2, v20_3_0_3, v20_3_0_6, v20_3_0_9, v20_3_0_9_div2, v20_3_1_1, v20_3_1_2, v20_5_0_0, v20_6_0_0, v20_6_0_2, v20_6_5_0, v20_6_5_0_dem, v20_6_5_0_dem2, v2_3, v30_0_0_2, v30_1_0_1, v30_1_0_3, v30_2_0_3, v3_0, v3_03, v3_1, v3_3_0_13, v4_0_0_0, v4_0_0_2, v4_1_0_12, v4_2_0_2, v4_2_1_0, v4_2_2_0]

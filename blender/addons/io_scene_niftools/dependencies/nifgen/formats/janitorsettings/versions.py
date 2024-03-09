from enum import Enum

from nifgen.base_version import VersionBase
from nifgen.formats.ovl_base.bitfields.VersionInfo import VersionInfo


def is_dla(context):
	if context.version == 15:
		return True


def set_dla(context):
	context.version = 15


def is_jwe(context):
	if context.version == 19 and context.user_version in (24724, 25108, 24596):
		return True


def set_jwe(context):
	context.version = 19
	context.user_version._value = 24724


def is_jwe2(context):
	if context.version == 20 and context.user_version in (24724, 25108, 24596):
		return True


def set_jwe2(context):
	context.version = 20
	context.user_version._value = 24724


def is_jwe2dev(context):
	if context.version == 20 and context.user_version in (24724, 25108, 24596) and context.is_dev == 1:
		return True


def set_jwe2dev(context):
	context.version = 20
	context.user_version._value = 24724
	context.is_dev = 1


def is_pc(context):
	if context.version == 18 and context.user_version in (8340, 8724, 8212) and context.version_flag == 8:
		return True


def set_pc(context):
	context.version = 18
	context.user_version._value = 8340
	context.version_flag = 8


def is_pz(context):
	if context.version == 19 and context.user_version in (8340, 8724, 8212):
		return True


def set_pz(context):
	context.version = 19
	context.user_version._value = 8340


def is_pz16(context):
	if context.version == 20 and context.user_version in (8340, 8724, 8212):
		return True


def set_pz16(context):
	context.version = 20
	context.user_version._value = 8340


def is_ztuac(context):
	if context.version == 17:
		return True


def set_ztuac(context):
	context.version = 17


games = Enum('Games', [('DISNEYLAND_ADVENTURES', 'Disneyland Adventures'), ('JURASSIC_WORLD_EVOLUTION', 'Jurassic World Evolution'), ('JURASSIC_WORLD_EVOLUTION_2', 'Jurassic World Evolution 2'), ('JURASSIC_WORLD_EVOLUTION_2_DEV', 'Jurassic World Evolution 2 Dev'), ('PLANET_COASTER', 'Planet Coaster'), ('PLANET_ZOO', 'Planet Zoo'), ('PLANET_ZOO_PRE_1_6', 'Planet Zoo pre-1.6'), ('ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION', 'Zoo Tycoon Ultimate Animal Collection'), ('UNKNOWN', 'Unknown Game')])


def get_game(context):
	if is_dla(context):
		return [games.DISNEYLAND_ADVENTURES]
	if is_jwe(context):
		return [games.JURASSIC_WORLD_EVOLUTION]
	if is_jwe2(context):
		return [games.JURASSIC_WORLD_EVOLUTION_2]
	if is_jwe2dev(context):
		return [games.JURASSIC_WORLD_EVOLUTION_2_DEV]
	if is_pc(context):
		return [games.PLANET_COASTER]
	if is_pz(context):
		return [games.PLANET_ZOO_PRE_1_6]
	if is_pz16(context):
		return [games.PLANET_ZOO]
	if is_ztuac(context):
		return [games.ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION]
	return [games.UNKNOWN]


def set_game(context, game):
	if isinstance(game, str):
		game = games(game)
	if game in {games.DISNEYLAND_ADVENTURES}:
		return set_dla(context)
	if game in {games.JURASSIC_WORLD_EVOLUTION}:
		return set_jwe(context)
	if game in {games.JURASSIC_WORLD_EVOLUTION_2}:
		return set_jwe2(context)
	if game in {games.JURASSIC_WORLD_EVOLUTION_2_DEV}:
		return set_jwe2dev(context)
	if game in {games.PLANET_COASTER}:
		return set_pc(context)
	if game in {games.PLANET_ZOO_PRE_1_6}:
		return set_pz(context)
	if game in {games.PLANET_ZOO}:
		return set_pz16(context)
	if game in {games.ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION}:
		return set_ztuac(context)


class JanitorsettingsVersion(VersionBase):

	_file_format = 'janitorsettings'
	_verattrs = ('version', 'user_version', 'version_flag')

	def __init__(self, *args, version=(), user_version=(), version_flag=(), **kwargs):
		super().__init__(*args, **kwargs)
		self.version = self._force_tuple(version)
		self.user_version = self._force_tuple(user_version)
		self.version_flag = self._force_tuple(version_flag)


dla = JanitorsettingsVersion(id='DLA', version=(15,), primary_games=[], all_games=[games.DISNEYLAND_ADVENTURES])
jwe = JanitorsettingsVersion(id='JWE', version=(19,), user_version=(VersionInfo.from_value(24724), VersionInfo.from_value(25108), VersionInfo.from_value(24596),), primary_games=[], all_games=[games.JURASSIC_WORLD_EVOLUTION])
jwe2 = JanitorsettingsVersion(id='JWE2', version=(20,), user_version=(VersionInfo.from_value(24724), VersionInfo.from_value(25108), VersionInfo.from_value(24596),), primary_games=[], all_games=[games.JURASSIC_WORLD_EVOLUTION_2])
jwe2dev = JanitorsettingsVersion(id='JWE2DEV', version=(20,), user_version=(VersionInfo.from_value(24724), VersionInfo.from_value(25108), VersionInfo.from_value(24596),), primary_games=[], all_games=[games.JURASSIC_WORLD_EVOLUTION_2_DEV])
pc = JanitorsettingsVersion(id='PC', version=(18,), user_version=(VersionInfo.from_value(8340), VersionInfo.from_value(8724), VersionInfo.from_value(8212),), version_flag=(8,), primary_games=[], all_games=[games.PLANET_COASTER])
pz = JanitorsettingsVersion(id='PZ', version=(19,), user_version=(VersionInfo.from_value(8340), VersionInfo.from_value(8724), VersionInfo.from_value(8212),), primary_games=[], all_games=[games.PLANET_ZOO_PRE_1_6])
pz16 = JanitorsettingsVersion(id='PZ16', version=(20,), user_version=(VersionInfo.from_value(8340), VersionInfo.from_value(8724), VersionInfo.from_value(8212),), primary_games=[], all_games=[games.PLANET_ZOO])
ztuac = JanitorsettingsVersion(id='ZTUAC', version=(17,), primary_games=[], all_games=[games.ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION])

available_versions = [dla, jwe, jwe2, jwe2dev, pc, pz, pz16, ztuac]

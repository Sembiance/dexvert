from enum import Enum

from nifgen.base_version import VersionBase
from nifgen.formats.ovl_base.bitfields.VersionInfo import VersionInfo


def is_dla(context):
	if context.version == 7:
		return True


def set_dla(context):
	context.version = 7


def is_jwe(context):
	if context.version in (47, 39):
		return True


def set_jwe(context):
	context.version = 47


def is_jwe2(context):
	if context.version in (52, 51):
		return True


def set_jwe2(context):
	context.version = 52


def is_jwe2dev(context):
	if context.version == 20 and context.user_version in (24724, 25108, 24596) and context.is_dev == 1:
		return True


def set_jwe2dev(context):
	context.version = 20
	context.user_version._value = 24724
	context.is_dev = 1


def is_pc(context):
	if context.version == 32:
		return True


def set_pc(context):
	context.version = 32


def is_pz(context):
	if context.version in (50, 48):
		return True


def set_pz(context):
	context.version = 50


def is_pz16(context):
	if context.version == 50:
		return True


def set_pz16(context):
	context.version = 50


def is_war(context):
	if context.version == 53:
		return True


def set_war(context):
	context.version = 53


def is_ztuac(context):
	if context.version == 13:
		return True


def set_ztuac(context):
	context.version = 13


def is_old(context):
	if context.version in (32, 13, 7):
		return True


def set_old(context):
	context.version = 32


games = Enum('Games', [('DISNEYLAND_ADVENTURES', 'Disneyland Adventures'), ('JURASSIC_WORLD_EVOLUTION', 'Jurassic World Evolution'), ('JURASSIC_WORLD_EVOLUTION_2', 'Jurassic World Evolution 2'), ('JURASSIC_WORLD_EVOLUTION_2_DEV', 'Jurassic World Evolution 2 Dev'), ('OLD', 'Old'), ('PLANET_COASTER', 'Planet Coaster'), ('PLANET_ZOO_ALL', 'Planet Zoo (all)'), ('PLANET_ZOO_LATEST', 'Planet Zoo (latest)'), ('WARHAMMER_RO_R', 'Warhammer RoR'), ('ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION', 'Zoo Tycoon Ultimate Animal Collection'), ('UNKNOWN', 'Unknown Game')])


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
		return [games.PLANET_ZOO_ALL]
	if is_pz16(context):
		return [games.PLANET_ZOO_LATEST]
	if is_war(context):
		return [games.WARHAMMER_RO_R]
	if is_ztuac(context):
		return [games.ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION]
	if is_old(context):
		return [games.OLD]
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
	if game in {games.PLANET_ZOO_ALL}:
		return set_pz(context)
	if game in {games.PLANET_ZOO_LATEST}:
		return set_pz16(context)
	if game in {games.WARHAMMER_RO_R}:
		return set_war(context)
	if game in {games.ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION}:
		return set_ztuac(context)
	if game in {games.OLD}:
		return set_old(context)


class Ms2Version(VersionBase):

	_file_format = 'ms2'
	_verattrs = ('version', 'user_version', 'version_flag')

	def __init__(self, *args, version=(), user_version=(), version_flag=(), **kwargs):
		super().__init__(*args, **kwargs)
		self.version = self._force_tuple(version)
		self.user_version = self._force_tuple(user_version)
		self.version_flag = self._force_tuple(version_flag)


dla = Ms2Version(id='DLA', version=(7,), primary_games=[], all_games=[games.DISNEYLAND_ADVENTURES])
jwe = Ms2Version(id='JWE', version=(47, 39,), primary_games=[], all_games=[games.JURASSIC_WORLD_EVOLUTION])
jwe2 = Ms2Version(id='JWE2', version=(52, 51,), primary_games=[], all_games=[games.JURASSIC_WORLD_EVOLUTION_2])
jwe2dev = Ms2Version(id='JWE2DEV', version=(20,), user_version=(VersionInfo.from_value(24724), VersionInfo.from_value(25108), VersionInfo.from_value(24596),), primary_games=[], all_games=[games.JURASSIC_WORLD_EVOLUTION_2_DEV])
pc = Ms2Version(id='PC', version=(32,), primary_games=[], all_games=[games.PLANET_COASTER])
pz = Ms2Version(id='PZ', version=(50, 48,), primary_games=[], all_games=[games.PLANET_ZOO_ALL])
pz16 = Ms2Version(id='PZ16', version=(50,), primary_games=[], all_games=[games.PLANET_ZOO_LATEST])
war = Ms2Version(id='WAR', version=(53,), primary_games=[], all_games=[games.WARHAMMER_RO_R])
ztuac = Ms2Version(id='ZTUAC', version=(13,), primary_games=[], all_games=[games.ZOO_TYCOON_ULTIMATE_ANIMAL_COLLECTION])
old = Ms2Version(id='old', version=(32, 13, 7,), primary_games=[], all_games=[games.OLD])

available_versions = [dla, jwe, jwe2, jwe2dev, pc, pz, pz16, war, ztuac, old]

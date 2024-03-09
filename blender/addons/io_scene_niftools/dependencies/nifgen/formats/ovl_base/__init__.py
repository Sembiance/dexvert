from nifgen.formats.ovl_base.imports import name_type_map
from nifgen.formats.ovl_base.bitfields.VersionInfo import VersionInfo


class OvlContext(object):
	def __init__(self):
		self.version = 0
		self.is_dev = 0
		self.user_version = VersionInfo()

	def __repr__(self):
		return f"{self.version} | {self.user_version}"

	@classmethod
	def to_xml(cls, elem, prop, instance, arg, template, debug):
		from nifgen.formats.ovl.versions import get_game
		elem.attrib[prop] = str(get_game(instance)[0])

	@classmethod
	def context_to_xml(cls, elem, prop, instance, arg, template, debug):
		from nifgen.formats.ovl.versions import get_game
		elem.attrib[prop] = str(get_game(instance)[0])

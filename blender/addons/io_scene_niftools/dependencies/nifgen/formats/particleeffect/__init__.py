from nifgen.formats.particleeffect.imports import name_type_map
from io import BytesIO
import os
import logging

from nifgen.formats.ovl_base import OvlContext
from nifgen.formats.particleeffect.compounds.ParticleEffectRoot import ParticleEffectRoot

logging.basicConfig(level=logging.DEBUG)


class ParticleEffectFile(ParticleEffectRoot):

	def __init__(self, ):
		pass

	def load(self, filepath, read_bytes=False, read_editable=False):
		self.filepath = filepath
		self._context = OvlContext()
		self.dir, self.name = os.path.split(os.path.normpath(filepath))
		self.read_editable = read_editable
		logging.debug(f"Reading {self.filepath}")
		self.particleeffect = ParticleEffectRoot.from_xml_file(self.filepath, self._context)


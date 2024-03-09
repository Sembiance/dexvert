import struct
import xml.etree.ElementTree as ET
import logging

import numpy as np

from nifgen.array import Array
from nifgen.base_struct import BaseStruct
from nifgen.formats.base.basic import ZString
from nifgen.formats.ovl_base.basic import ZStringObfuscated

ZERO = b"\x00"
# these attributes present on the MemStruct will not be stored on the XML
SKIPS = ("_context", "arg", "name", "io_start", "io_size", "template")
POOL_TYPE = "pool_type"
DTYPE = "dtype"
XML_STR = "xml_string"
DEPENDENCY_TAG = "dependency"

from nifgen.base_struct import BaseStruct
from nifgen.formats.ovl_base.imports import name_type_map


class Pointer(BaseStruct):

	"""
	a pointer in an ovl memory layout, can point to a struct or a dependency entry
	"""

	__name__ = 'Pointer'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'pool_index', name_type_map['Int'], (0, None), (False, -1), (None, None)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'pool_index', name_type_map['Int'], (0, None), (False, -1)
		yield 'data_offset', name_type_map['Uint'], (0, None), (False, None)

	def __init__(self, context, arg=0, template=None, set_default=True):
		super().__init__(context, arg, template, set_default=False)
		# set to -1 here so that read_ptr doesn't get a wrong frag by chance if the entry has not been read -> get at 0
		self.io_start = -1
		self.target_offset = -1
		self.pool_index = 0
		self.data_offset = 0
		self.data = None
		self.frag = None
		self.link = None
		self.target_pool = None
		self.pool_type = None
		if set_default:
			self.set_defaults()

	@property
	def has_data(self):
		"""Returns True if it has data"""
		return bool(self.data)

	@classmethod
	def get_fields_str(cls, instance, indent=0):
		s = ''
		s += f'\n	* pool_index = {instance.pool_index.__repr__()}'
		s += f'\n	* data_offset = {instance.data_offset.__repr__()}'
		s += f'\n	* data = {instance.data.__repr__()}'
		return s

	def read_ptr(self, pool):
		"""Looks up the address of the pointer, checks if a frag points to pointer and reads the data at its address as
		the specified template."""
		# find the frag entry with matching link_ptr.data_offset
		link = pool.offset_2_link.get(self.io_start, None)
		# pointer may be a nullptr, so ignore
		if not link:
			# print("is a nullptr")
			return
		# it is a dependency
		if isinstance(link, str):
			# store dependency name
			self.data = link
		else:
			# now read an instance of template class at the offset
			self.target_pool, self.target_offset = link
			self.link = link
			# we are now (potentially) in a new pool
			self.pool_type = self.target_pool.type
			stream = self.target_pool.stream_at(self.target_offset)
			self.read_template(stream)

	def read_template(self, stream):
		if self.template:
			self.data = self.template.from_stream(stream, self.context, self.arg)

	def write_ptr(self, loader, src_pool):
		# when generated from XML, the pool type is stored as metadata
		# it's not stored in binary, so for those, keep the root pool type
		if self.pool_type is None:
			self.pool_type = src_pool.type
		self.target_pool = loader.get_pool(self.pool_type)
		# usually we add a pointer for empty arrays
		# assert self.has_data
		# seek to end, set data_offset, write
		stream, self.target_offset = self.target_pool.align_write(self.data)
		# if bytes have been set (usually manually), don't ask, just write
		if isinstance(self.data, (bytes, bytearray)):
			stream.write(self.data)
		else:
			try:
				assert self.template is not None
				if self.data is None:
					logging.info(f"Can't write None for class {self.template}")
				elif isinstance(self.data, (Array, np.ndarray)):
					Array.to_stream(self.data, stream, self.context, dtype=self.template)
				else:
					self.template.to_stream(self.data, stream, self.context)
			except TypeError:
				raise TypeError(f"Failed to write pointer data {self.data} type: {type(self.data)} as {self.template}")
			except struct.error:
				raise TypeError(f"Failed to write pointer data {self.data} type: {type(self.data)} as {self.template}")
		# nothing has been written, so set to None to move link to end of pool on saving
		if self.target_offset == stream.tell():
			self.target_offset = None
		else:
			# only store these if the pointer had valid data
			self.target_pool.offsets.add(self.target_offset)
			# store size in size_map
			self.target_pool.size_map[self.target_offset] = self.target_pool.data.tell() - self.target_offset
		# the data has been written, now store the links
		loader.attach_frag_to_ptr(src_pool, self.io_start, self.target_pool, self.target_offset)

	@classmethod
	def to_xml(cls, elem, prop, instance, arg, template, debug):
		"""Adds this struct to 'elem', recursively"""
		sub = ET.SubElement(elem, prop)
		cls.pool_type_to_xml(sub, instance, debug)
		if instance.has_data:
			pool = instance.target_pool
			# always set this to support xml references
			# elem.attrib["id"] = f"{pool.i} | {instance.target_offset}"
			# xml string
			if prop == XML_STR:
				sub.append(ET.fromstring(instance.data))
			else:
				cls._to_xml(instance, sub, debug)

	@classmethod
	def pool_type_to_xml(cls, elem, instance, debug):
		"""Sets the pool type of instance to elem's attrib"""
		if instance.link and isinstance(instance.link, tuple):
			pool = instance.target_pool
			if debug:
				elem.set("_address", f"{pool.i} | {instance.target_offset}")
				elem.set("_size", f"{pool.size_map.get(instance.target_offset, -1)}")
			cls._set_pool_type(elem, pool.type, instance.template)
		elif hasattr(instance, POOL_TYPE):
			if instance.pool_type is not None:
				cls._set_pool_type(elem, instance.pool_type, instance.template)

	@staticmethod
	def _set_pool_type(elem, pool_type, template):
		"""Set the pool type, unless it is obvious"""
		# if template not in (ZString, ZStringObfuscated):
		if pool_type != 2:
			elem.set(POOL_TYPE, f"{pool_type}")

	@classmethod
	def _to_xml(cls, instance, elem, debug):
		"""Assigns data self to xml elem"""
		# catch Zstr Pointers and dependencies (template=None)
		if isinstance(instance.data, str):
			elem.text = instance.data
		else:
			if instance.template is not None and instance.has_data:
				instance.template._to_xml(instance.data, elem, debug)

	@classmethod
	def pool_type_from_xml(cls, elem, instance):
		if POOL_TYPE in elem.attrib:
			instance.pool_type = int(elem.attrib[POOL_TYPE])
			# logging.debug(f"Set pool type {instance.pool_type} for pointer {elem.tag}")
		else:
			instance.pool_type = 2

	@classmethod
	def from_xml(cls, target, elem, prop, arg, template):
		"""Creates object for parent object 'target', from parent element elem."""
		# create Pointer instance
		instance = cls(target.context, arg, template, set_default=False)
		# check if the pointer holds data
		sub = elem.find(f'./{prop}')
		if sub is None:
			logging.warning(f"Missing sub-element '{prop}' on XML element '{elem.tag}'")
			# we absolutely do need to create the instance so that the structure of the parent struct remains intact
			instance.data = None
		else:
			# store the pointer's pool type
			cls.pool_type_from_xml(sub, instance)
			# process the pointer's data
			if prop == XML_STR:
				instance.data = ET.tostring(sub[0], encoding="unicode").replace("\t", "").replace("\n", "")
			else:
				cls._from_xml(instance, sub)
		return instance

	@classmethod
	def _from_xml(cls, instance, elem):
		try:
			if instance.template is None:
				if DEPENDENCY_TAG in elem.tag:
					if elem.text and elem.text != "None":
						logging.debug(f"Setting dependency {type(instance).__name__}.data = {elem.text}")
						instance.data = elem.text
				return
			elif instance.template in (ZString, ZStringObfuscated):
				if elem.text:
					instance.data = elem.text
			else:
				instance.data = instance.template(instance.context, instance.arg, None)
				instance.template._from_xml(instance.data, elem)
			return instance
		except:
			logging.exception(f"Error on ptr {elem} {elem.attrib}")
			# raise


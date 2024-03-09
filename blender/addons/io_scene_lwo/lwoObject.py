# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import os
import struct
import chunk
import re
from glob import glob
from pprint import pprint
from collections import OrderedDict

DEBUG = False

class lwoNoImageFoundException(Exception):
	pass


class lwoUnsupportedFileException(Exception):
	pass


class _lwo_base:
	def __eq__(self, x):
		if not isinstance(x, self.__class__):
			return False
		for k in self.__slots__:
			a = getattr(self, k)
			b = getattr(x, k)
			if not a == b:
				print(f"{k} mismatch:")
				print(f"\t{a} != {b}")
				return False
		return True

	@property
	def dict(self):
		d = OrderedDict()
		for k in self.__slots__:
			d[k] = getattr(self, k)
		return d

	def __repr__(self):
		return str(self.dict)


class _obj_layer(_lwo_base):
	__slots__ = (
		"name",
		"index",
		"parent_index",
		"pivot",
		"pols",
		"bones",
		"bone_names",
		"bone_rolls",
		"pnts",
		"vnorms",
		"lnorms",
		"wmaps",
		"colmaps",
		"uvmaps_vmad",
		"uvmaps_vmap",
		"morphs",
		"edge_weights",
		"surf_tags",
		"has_subds",
	)

	def __init__(self):
		self.name = ""
		self.index = -1
		self.parent_index = -1
		self.pivot = [0, 0, 0]
		self.pols = []
		self.bones = []
		self.bone_names = {}
		self.bone_rolls = {}
		self.pnts = []
		self.vnorms = {}
		self.lnorms = {}
		self.wmaps = {}
		self.colmaps = {}
		self.uvmaps_vmad = {}
		self.uvmaps_vmap = {}
		self.morphs = {}
		self.edge_weights = {}
		self.surf_tags = {}
		self.has_subds = False


class _obj_surf(_lwo_base):
	__slots__ = (
		"name",
		"source_name",
		"colr",
		"diff",
		"lumi",
		"spec",
		"refl",
		"rblr",
		"tran",
		"rind",
		"tblr",
		"trnl",
		"glos",
		"shrp",
		"bump",
		"strs",
		"smooth",
		"textures",
		"textures_5",
	)

	def __init__(self):
		self.name = "Default"
		self.source_name = ""
		self.colr = [1.0, 1.0, 1.0]
		self.diff = 1.0  # Diffuse
		self.lumi = 0.0  # Luminosity
		self.spec = 0.0  # Specular
		self.refl = 0.0  # Reflectivity
		self.rblr = 0.0  # Reflection Bluring
		self.tran = 0.0  # Transparency (the opposite of Blender's Alpha value)
		self.rind = 1.0  # RT Transparency IOR
		self.tblr = 0.0  # Refraction Bluring
		self.trnl = 0.0  # Translucency
		self.glos = 0.4  # Glossiness
		self.shrp = 0.0  # Diffuse Sharpness
		self.bump = 1.0  # Bump
		self.strs = 0.0  # Smooth Threshold
		self.smooth = False  # Surface Smoothing
		self.textures = {}  # Textures list
		self.textures_5 = []  # Textures list for LWOB

	def lwoprint(self):  # debug: no cover
		print(f"SURFACE")
		print(f"Surface Name:       {self.name}")
		print(f"Color:              {int(self.colr[0]*256)} {int(self.colr[1]*256)} {int(self.colr[2]*256)}")
		print(f"Luminosity:         {self.lumi*100:>8.1f}%")
		print(f"Diffuse:            {self.diff*100:>8.1f}%")
		print(f"Specular:           {self.spec*100:>8.1f}%")
		print(f"Glossiness:         {self.glos*100:>8.1f}%")
		print(f"Reflection:         {self.refl*100:>8.1f}%")
		print(f"Transparency:       {self.tran*100:>8.1f}%")
		print(f"Refraction Index:   {self.rind:>8.1f}")
		print(f"Translucency:       {self.trnl*100:>8.1f}%")
		print(f"Bump:               {self.bump*100:>8.1f}%")
		print(f"Smoothing:          {self.smooth:>8}")
		print(f"Smooth Threshold:   {self.strs*100:>8.1f}%")
		print(f"Reflection Bluring: {self.rblr*100:>8.1f}%")
		print(f"Refraction Bluring: {self.tblr*100:>8.1f}%")
		print(f"Diffuse Sharpness:  {self.shrp*100:>8.1f}%")
		print()
		for textures_type in self.textures.keys():
			print(textures_type)
			for texture in self.textures[textures_type]:
				texture.lwoprint(indent=1)


class _surf_texture(_lwo_base):
	__slots__ = (
		"opac",
		"opactype",
		"enab",
		"clipid",
		"projection",
		"enab",
		"uvname",
		"channel",
		"type",
		"func",
		"image",
		"nega",
	)

	def __init__(self):
		self.clipid = 1
		self.opac = 1.0
		self.opactype = 0
		self.enab = True
		self.projection = 5
		self.uvname = "UVMap"
		self.channel = "COLR"
		self.type = "IMAP"
		self.func = None
		self.image = None
		self.nega = None

	def lwoprint(self, indent=0):  # debug: no cover
		print(f"TEXTURE")
		print(f"ClipID:         {self.clipid}")
		print(f"Opacity:        {self.opac*100:.1f}%")
		print(f"Opacity Type:   {self.opactype}")
		print(f"Enabled:        {self.enab}")
		print(f"Projection:     {self.projection}")
		print(f"UVname:         {self.uvname}")
		print(f"Channel:        {self.channel}")
		print(f"Type:           {self.type}")
		print(f"Function:       {self.func}")
		print(f"Image:          {self.image}")
		print()


class _surf_texture_5(_lwo_base):
	__slots__ = ("id", "image", "X", "Y", "Z")

	def __init__(self):
		self.id = id(self)
		self.image = None
		self.X = False
		self.Y = False
		self.Z = False


def read_lwostring(raw_name):
	"""Parse a zero-padded string."""

	i = raw_name.find(b"\0")
	name_len = i + 1
	if name_len % 2 == 1:  # Test for oddness.
		name_len += 1

	if i > 0:
		# Some plugins put non-text strings in the tags chunk.
		name = raw_name[0:i].decode("utf-8", "ignore")
	else:
		name = ""

	return name, name_len


def read_vx(pointdata):
	"""Read a variable-length index."""
	if pointdata[0] != 255:
		index = pointdata[0] * 256 + pointdata[1]
		size = 2
	else:
		index = pointdata[1] * 65536 + pointdata[2] * 256 + pointdata[3]
		size = 4

	return index, size


def read_tags(tag_bytes, lwo):
	"""Read the object's Tags chunk."""
	offset = 0
	chunk_len = len(tag_bytes)

	while offset < chunk_len:
		tag, tag_len = read_lwostring(tag_bytes[offset:])
		offset += tag_len
		lwo.tags.append(tag)


def read_layr(layr_bytes, object_layers, load_hidden):
	"""Read the object's layer data."""
	new_layr = _obj_layer()
	new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])

	if flags > 0 and not load_hidden:
		return False

	print("Reading Object Layer")
	offset = 4
	pivot = struct.unpack(">fff", layr_bytes[offset : offset + 12])
	# Swap Y and Z to match Blender's pitch.
	new_layr.pivot = [pivot[0], pivot[2], pivot[1]]
	offset += 12
	layr_name, name_len = read_lwostring(layr_bytes[offset:])
	offset += name_len

	if layr_name:
		new_layr.name = layr_name
	else:
		new_layr.name = "Layer %d" % (new_layr.index + 1)

	if len(layr_bytes) == offset + 2:
		(new_layr.parent_index,) = struct.unpack(">h", layr_bytes[offset : offset + 2])

	object_layers.append(new_layr)
	return True


def read_layr_5(layr_bytes, object_layers):
	"""Read the object's layer data."""
	# XXX: Need to check what these two exactly mean for a LWOB/LWLO file.
	new_layr = _obj_layer()
	new_layr.index, flags = struct.unpack(">HH", layr_bytes[0:4])

	print("Reading Object Layer")
	offset = 4
	layr_name, name_len = read_lwostring(layr_bytes[offset:])
	offset += name_len

	if name_len > 2 and layr_name != "noname":
		new_layr.name = layr_name
	else:
		# new_layr.name = f"Layer {new_layr.index}"
		new_layr.name = "Layer {}".format(new_layr.index)

	object_layers.append(new_layr)


def read_pnts(pnt_bytes, object_layers):
	"""Read the layer's points."""
	print(f"\tReading Layer ({object_layers[-1].name }) Points")
	offset = 0
	chunk_len = len(pnt_bytes)

	while offset < chunk_len:
		pnts = struct.unpack(">fff", pnt_bytes[offset : offset + 12])
		offset += 12
		# Re-order the points so that the mesh has the right pitch,
		# the pivot already has the correct order.
		pnts = [
			pnts[0] - object_layers[-1].pivot[0],
			pnts[2] - object_layers[-1].pivot[1],
			pnts[1] - object_layers[-1].pivot[2],
		]
		object_layers[-1].pnts.append(pnts)


def read_weightmap(weight_bytes, object_layers):
	"""Read a weight map's values."""
	chunk_len = len(weight_bytes)
	offset = 2
	name, name_len = read_lwostring(weight_bytes[offset:])
	offset += name_len
	weights = []

	while offset < chunk_len:
		pnt_id, pnt_id_len = read_vx(weight_bytes[offset : offset + 4])
		offset += pnt_id_len
		(value,) = struct.unpack(">f", weight_bytes[offset : offset + 4])
		offset += 4
		weights.append([pnt_id, value])

	object_layers[-1].wmaps[name] = weights


def read_morph(morph_bytes, object_layers, is_abs):
	"""Read an endomorph's relative or absolute displacement values."""
	chunk_len = len(morph_bytes)
	offset = 2
	name, name_len = read_lwostring(morph_bytes[offset:])
	offset += name_len
	deltas = []

	while offset < chunk_len:
		pnt_id, pnt_id_len = read_vx(morph_bytes[offset : offset + 4])
		offset += pnt_id_len
		pos = struct.unpack(">fff", morph_bytes[offset : offset + 12])
		offset += 12
		pnt = object_layers[-1].pnts[pnt_id]

		if is_abs:
			deltas.append([pnt_id, pos[0], pos[2], pos[1]])
		else:
			# Swap the Y and Z to match Blender's pitch.
			deltas.append([pnt_id, pnt[0] + pos[0], pnt[1] + pos[2], pnt[2] + pos[1]])

		object_layers[-1].morphs[name] = deltas


def read_colmap(col_bytes, object_layers):
	"""Read the RGB or RGBA color map."""
	chunk_len = len(col_bytes)
	(dia,) = struct.unpack(">H", col_bytes[0:2])
	offset = 2
	name, name_len = read_lwostring(col_bytes[offset:])
	offset += name_len
	colors = {}

	if dia == 3:
		while offset < chunk_len:
			pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
			offset += pnt_id_len
			col = struct.unpack(">fff", col_bytes[offset : offset + 12])
			offset += 12
			colors[pnt_id] = (col[0], col[1], col[2])
	elif dia == 4:
		while offset < chunk_len:
			pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
			offset += pnt_id_len
			col = struct.unpack(">ffff", col_bytes[offset : offset + 16])
			offset += 16
			colors[pnt_id] = (col[0], col[1], col[2])

	if name in object_layers[-1].colmaps:
		if "PointMap" in object_layers[-1].colmaps[name]:
			object_layers[-1].colmaps[name]["PointMap"].update(colors)
		else:
			object_layers[-1].colmaps[name]["PointMap"] = colors
	else:
		object_layers[-1].colmaps[name] = dict(PointMap=colors)


def read_normmap(norm_bytes, object_layers):
	"""Read vertex normal maps."""
	chunk_len = len(norm_bytes)
	offset = 2
	name, name_len = read_lwostring(norm_bytes[offset:])
	offset += name_len
	vnorms = {}

	while offset < chunk_len:
		pnt_id, pnt_id_len = read_vx(norm_bytes[offset : offset + 4])
		offset += pnt_id_len
		norm = struct.unpack(">fff", norm_bytes[offset : offset + 12])
		offset += 12
		vnorms[pnt_id] = [norm[0], norm[2], norm[1]]

	object_layers[-1].vnorms = vnorms


def read_color_vmad(col_bytes, object_layers, last_pols_count):
	"""Read the Discontinuous (per-polygon) RGB values."""
	chunk_len = len(col_bytes)
	(dia,) = struct.unpack(">H", col_bytes[0:2])
	offset = 2
	name, name_len = read_lwostring(col_bytes[offset:])
	offset += name_len
	colors = {}
	abs_pid = len(object_layers[-1].pols) - last_pols_count

	if dia == 3:
		while offset < chunk_len:
			pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
			offset += pnt_id_len
			pol_id, pol_id_len = read_vx(col_bytes[offset : offset + 4])
			offset += pol_id_len

			# The PolyID in a VMAD can be relative, this offsets it.
			pol_id += abs_pid
			col = struct.unpack(">fff", col_bytes[offset : offset + 12])
			offset += 12
			if pol_id in colors:
				colors[pol_id][pnt_id] = (col[0], col[1], col[2])
			else:
				colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})
	elif dia == 4:
		while offset < chunk_len:
			pnt_id, pnt_id_len = read_vx(col_bytes[offset : offset + 4])
			offset += pnt_id_len
			pol_id, pol_id_len = read_vx(col_bytes[offset : offset + 4])
			offset += pol_id_len

			pol_id += abs_pid
			col = struct.unpack(">ffff", col_bytes[offset : offset + 16])
			offset += 16
			if pol_id in colors:
				colors[pol_id][pnt_id] = (col[0], col[1], col[2])
			else:
				colors[pol_id] = dict({pnt_id: (col[0], col[1], col[2])})

	if name in object_layers[-1].colmaps:
		if "FaceMap" in object_layers[-1].colmaps[name]:
			object_layers[-1].colmaps[name]["FaceMap"].update(colors)
		else:
			object_layers[-1].colmaps[name]["FaceMap"] = colors
	else:
		object_layers[-1].colmaps[name] = dict(FaceMap=colors)


def read_uvmap(uv_bytes, object_layers):
	"""Read the simple UV coord values."""
	chunk_len = len(uv_bytes)
	offset = 2
	name, name_len = read_lwostring(uv_bytes[offset:])
	offset += name_len
	uv_coords = {}

	while offset < chunk_len:
		pnt_id, pnt_id_len = read_vx(uv_bytes[offset : offset + 4])
		offset += pnt_id_len
		pos = struct.unpack(">ff", uv_bytes[offset : offset + 8])
		offset += 8
		uv_coords[pnt_id] = (pos[0], pos[1])

	if name in object_layers[-1].uvmaps_vmap:
		if "PointMap" in object_layers[-1].uvmaps_vmap[name]:
			object_layers[-1].uvmaps_vmap[name]["PointMap"].update(uv_coords)
		else:
			object_layers[-1].uvmaps_vmap[name]["PointMap"] = uv_coords
	else:
		object_layers[-1].uvmaps_vmap[name] = dict(PointMap=uv_coords)


def read_uv_vmad(uv_bytes, object_layers, last_pols_count):
	"""Read the Discontinuous (per-polygon) uv values."""
	chunk_len = len(uv_bytes)
	offset = 2
	name, name_len = read_lwostring(uv_bytes[offset:])
	offset += name_len
	uv_coords = {}
	abs_pid = len(object_layers[-1].pols) - last_pols_count

	while offset < chunk_len:
		pnt_id, pnt_id_len = read_vx(uv_bytes[offset : offset + 4])
		offset += pnt_id_len
		pol_id, pol_id_len = read_vx(uv_bytes[offset : offset + 4])
		offset += pol_id_len

		pol_id += abs_pid
		pos = struct.unpack(">ff", uv_bytes[offset : offset + 8])
		offset += 8
		if pol_id in uv_coords:
			uv_coords[pol_id][pnt_id] = (pos[0], pos[1])
		else:
			uv_coords[pol_id] = dict({pnt_id: (pos[0], pos[1])})

	if name in object_layers[-1].uvmaps_vmad:
		if "FaceMap" in object_layers[-1].uvmaps_vmad[name]:
			object_layers[-1].uvmaps_vmad[name]["FaceMap"].update(uv_coords)
		else:
			object_layers[-1].uvmaps_vmad[name]["FaceMap"] = uv_coords
	else:
		object_layers[-1].uvmaps_vmad[name] = dict(FaceMap=uv_coords)


def read_weight_vmad(ew_bytes, object_layers):
	"""Read the VMAD Weight values."""
	chunk_len = len(ew_bytes)
	offset = 2
	name, name_len = read_lwostring(ew_bytes[offset:])
	if name != "Edge Weight":
		return  # We just want the Catmull-Clark edge weights

	offset += name_len
	# Some info: LW stores a face's points in a clock-wize order (with the
	# normal pointing at you). This gives edges a 'direction' which is used
	# when it comes to storing CC edge weight values. The weight is given
	# to the point preceding the edge that the weight belongs to.
	while offset < chunk_len:
		pnt_id, pnt_id_len = read_vx(ew_bytes[offset : offset + 4])
		offset += pnt_id_len
		pol_id, pol_id_len = read_vx(ew_bytes[offset : offset + 4])
		offset += pol_id_len
		(weight,) = struct.unpack(">f", ew_bytes[offset : offset + 4])
		offset += 4

		face_pnts = object_layers[-1].pols[pol_id]
		try:
			# Find the point's location in the polygon's point list
			first_idx = face_pnts.index(pnt_id)
		except:
			continue

		# Then get the next point in the list, or wrap around to the first
		if first_idx == len(face_pnts) - 1:
			second_pnt = face_pnts[0]
		else:
			second_pnt = face_pnts[first_idx + 1]

		object_layers[-1].edge_weights["{0} {1}".format(second_pnt, pnt_id)] = weight


def read_normal_vmad(norm_bytes, object_layers):
	"""Read the VMAD Split Vertex Normals"""
	chunk_len = len(norm_bytes)
	offset = 2
	name, name_len = read_lwostring(norm_bytes[offset:])
	lnorms = {}
	offset += name_len

	while offset < chunk_len:
		pnt_id, pnt_id_len = read_vx(norm_bytes[offset : offset + 4])
		offset += pnt_id_len
		pol_id, pol_id_len = read_vx(norm_bytes[offset : offset + 4])
		offset += pol_id_len
		norm = struct.unpack(">fff", norm_bytes[offset : offset + 12])
		offset += 12
		if not (pol_id in lnorms.keys()):
			lnorms[pol_id] = []
		lnorms[pol_id].append([pnt_id, norm[0], norm[2], norm[1]])

	print(f"LENGTH {len(lnorms.keys())}")
	object_layers[-1].lnorms = lnorms


def read_pols(pol_bytes, object_layers):
	"""Read the layer's polygons, each one is just a list of point indexes."""
	print(f"\tReading Layer ({object_layers[-1].name}) Polygons")
	offset = 0
	pols_count = len(pol_bytes)
	old_pols_count = len(object_layers[-1].pols)

	while offset < pols_count:
		(pnts_count,) = struct.unpack(">H", pol_bytes[offset : offset + 2])
		offset += 2
		all_face_pnts = []
		for j in range(pnts_count):
			face_pnt, data_size = read_vx(pol_bytes[offset : offset + 4])
			offset += data_size
			all_face_pnts.append(face_pnt)
		all_face_pnts.reverse()  # correct normals

		object_layers[-1].pols.append(all_face_pnts)

	return len(object_layers[-1].pols) - old_pols_count


def read_pols_5(pol_bytes, object_layers):
	"""
	Read the polygons, each one is just a list of point indexes.
	But it also includes the surface index.
	"""
	print(f"\tReading Layer ({object_layers[-1].name}) Polygons")
	offset = 0
	chunk_len = len(pol_bytes)
	old_pols_count = len(object_layers[-1].pols)
	poly = 0

	while offset < chunk_len:
		(pnts_count,) = struct.unpack(">H", pol_bytes[offset : offset + 2])
		offset += 2
		all_face_pnts = []
		for j in range(pnts_count):
			(face_pnt,) = struct.unpack(">H", pol_bytes[offset : offset + 2])
			offset += 2
			all_face_pnts.append(face_pnt)
		all_face_pnts.reverse()

		object_layers[-1].pols.append(all_face_pnts)
		(sid,) = struct.unpack(">h", pol_bytes[offset : offset + 2])
		offset += 2
		sid = abs(sid) - 1
		if sid not in object_layers[-1].surf_tags:
			object_layers[-1].surf_tags[sid] = []
		object_layers[-1].surf_tags[sid].append(poly)
		poly += 1

	return len(object_layers[-1].pols) - old_pols_count


def read_bones(bone_bytes, lwo):
	"""Read the layer's skelegons."""
	# print(f"\tReading Layer ({object_layers[-1].name}) Bones")
	offset = 0
	bones_count = len(bone_bytes)

	while offset < bones_count:
		(pnts_count,) = struct.unpack(">H", bone_bytes[offset : offset + 2])
		offset += 2
		all_bone_pnts = []
		for j in range(pnts_count):
			bone_pnt, data_size = read_vx(bone_bytes[offset : offset + 4])
			offset += data_size
			all_bone_pnts.append(bone_pnt)

		lwo.layers[-1].bones.append(all_bone_pnts)


def read_bone_tags(tag_bytes, lwo, type):
	"""Read the bone name or roll tags."""
	offset = 0
	chunk_len = len(tag_bytes)

	if type == "BONE":
		bone_dict = lwo.layers[-1].bone_names
	elif type == "BNUP":
		bone_dict = lwo.layers[-1].bone_rolls
	else:
		return

	while offset < chunk_len:
		pid, pid_len = read_vx(tag_bytes[offset : offset + 4])
		offset += pid_len
		(tid,) = struct.unpack(">H", tag_bytes[offset : offset + 2])
		offset += 2
		bone_dict[pid] = lwo.tags[tid]


def read_surf_tags(tag_bytes, object_layers, last_pols_count):
	"""Read the list of PolyIDs and tag indexes."""
	print(f"\tReading Layer ({object_layers[-1].name}) Surface Assignments")
	offset = 0
	chunk_len = len(tag_bytes)

	# Read in the PolyID/Surface Index pairs.
	abs_pid = len(object_layers[-1].pols) - last_pols_count
	if 0 == len(object_layers[-1].pols):
		return
	if abs_pid < 0:
		raise Exception(len(object_layers[-1].pols), last_pols_count, object_layers[-1].pols)
	while offset < chunk_len:
		pid, pid_len = read_vx(tag_bytes[offset : offset + 4])
		offset += pid_len
		(sid,) = struct.unpack(">H", tag_bytes[offset : offset + 2])
		offset += 2
		if sid not in object_layers[-1].surf_tags:
			object_layers[-1].surf_tags[sid] = []
		object_layers[-1].surf_tags[sid].append(pid + abs_pid)


def read_clip(clip_bytes, lwo):
	"""Read texture clip path"""
	c_id = struct.unpack(">L", clip_bytes[0:4])[0]
	orig_path, path_len = read_lwostring(clip_bytes[10:])
	lwo.clips[c_id] = orig_path


def read_texture(surf_bytes, offset, subchunk_len, debug=False):
	texture = _surf_texture()
	ordinal, ord_len = read_lwostring(surf_bytes[offset + 4 :])
	suboffset = 6 + ord_len
	while suboffset < subchunk_len:
		(subsubchunk_name,) = struct.unpack(
			"4s", surf_bytes[offset + suboffset : offset + suboffset + 4]
		)
		suboffset += 4
		(subsubchunk_len,) = struct.unpack(
			">H", surf_bytes[offset + suboffset : offset + suboffset + 2]
		)
		suboffset += 2
		if subsubchunk_name == b"CHAN":
			(texture.channel,) = struct.unpack(
				"4s", surf_bytes[offset + suboffset : offset + suboffset + 4],
			)
			texture.channel = texture.channel.decode("ascii")
		elif subsubchunk_name == b"OPAC":
			(texture.opactype,) = struct.unpack(
				">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
			)
			(texture.opac,) = struct.unpack(
				">f", surf_bytes[offset + suboffset + 2 : offset + suboffset + 6],
			)
			# print("opactype",opactype)
		elif subsubchunk_name == b"ENAB":
			(texture.enab,) = struct.unpack(
				">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
			)
		elif subsubchunk_name == b"IMAG":
			(texture.clipid,) = struct.unpack(
				">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
			)
		elif subsubchunk_name == b"PROJ":
			(texture.projection,) = struct.unpack(
				">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
			)
		elif subsubchunk_name == b"VMAP":
			texture.uvname, name_len = read_lwostring(surf_bytes[offset + suboffset :])
			# print(f"VMAP {texture.uvname} {name_len}")
		elif subsubchunk_name == b"FUNC":  # This is the procedural
			texture.func, name_len = read_lwostring(surf_bytes[offset + suboffset :])
		elif subsubchunk_name == b"NEGA":
			(texture.nega,) = struct.unpack(
				">H", surf_bytes[offset + suboffset : offset + suboffset + 2],
			)
		elif subsubchunk_name == b"TMAP":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name} {subchunk_len}")
		#                 xx, = struct.unpack(
		#                     ">H",
		#                     surf_bytes[offset + suboffset:offset + suboffset + 2],
		#                 )
		#                 print(xx)
		elif subsubchunk_name == b"AXIS":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name} {subchunk_len}")
		#                 xx,= struct.unpack(
		#                     ">H",
		#                     surf_bytes[offset + suboffset:offset + suboffset + 2],
		#                 )
		#                 print(xx)
		elif subsubchunk_name == b"WRAP":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"WRPW":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"WRPH":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"AAST":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"PIXB":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"VALU":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"TAMP":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"STCK":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"PNAM":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"INAM":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"GRST":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"GREN":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"GRPT":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"IKEY":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		elif subsubchunk_name == b"FKEY":
			if DEBUG:
				print(f"SubSubBlock: {subsubchunk_name}")
		else:
			print(f"Unimplemented SubSubBlock: {subsubchunk_name}")
			if DEBUG:
				raise Exception("Unimplemented SubSubBlock: {}".format(subsubchunk_name))
		suboffset += subsubchunk_len
	return texture


def read_surf(surf_bytes, lwo):
	"""Read the object's surface data."""
	if len(lwo.surfs) == 0:
		print("Reading Object Surfaces")

	surf = _obj_surf()
	name, name_len = read_lwostring(surf_bytes)
	if len(name) != 0:
		surf.name = name

	# We have to read this, but we won't use it...yet.
	s_name, s_name_len = read_lwostring(surf_bytes[name_len:])
	offset = name_len + s_name_len
	block_size = len(surf_bytes)
	while offset < block_size:
		(subchunk_name,) = struct.unpack("4s", surf_bytes[offset : offset + 4])
		offset += 4
		(subchunk_len,) = struct.unpack(">H", surf_bytes[offset : offset + 2])
		offset += 2

		# Now test which subchunk it is.
		if subchunk_name == b"COLR":
			surf.colr = struct.unpack(">fff", surf_bytes[offset : offset + 12])
			# Don't bother with any envelopes for now.

		elif subchunk_name == b"DIFF":
			(surf.diff,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"LUMI":
			(surf.lumi,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"SPEC":
			(surf.spec,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"REFL":
			(surf.refl,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"RBLR":
			(surf.rblr,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"TRAN":
			(surf.tran,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"RIND":
			(surf.rind,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"TBLR":
			(surf.tblr,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"TRNL":
			(surf.trnl,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"GLOS":
			(surf.glos,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"SHRP":
			(surf.shrp,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"SMAN":
			(s_angle,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
			# print(s_angle)
			if s_angle > 0.0:
				surf.smooth = True
		elif subchunk_name == b"BUMP":
			(surf.bump,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"BLOK":
			(block_type,) = struct.unpack("4s", surf_bytes[offset : offset + 4])
			texture = None
			if block_type == b"IMAP" or block_type == b"PROC" \
			or block_type == b"SHDR" or block_type == b"GRAD":
				# print(surf.name, block_type)
				texture = read_texture(surf_bytes, offset, subchunk_len)
			else:
				print(f"Unimplemented texture type: {block_type}")
				if DEBUG:
					raise Exception ("Unimplemented texture type: {}".format(block_type))
			if None is not texture:
				texture.type = block_type.decode("ascii")
				if texture.channel not in surf.textures.keys():
					surf.textures[texture.channel] = []
				surf.textures[texture.channel].append(texture)
		elif subchunk_name == b"VERS":
			pass
		elif subchunk_name == b"NODS":
			pass
		elif subchunk_name == b"GVAL":
			pass
		elif subchunk_name == b"NVSK":
			pass
		elif subchunk_name == b"CLRF":
			pass
		elif subchunk_name == b"CLRH":
			pass
		elif subchunk_name == b"ADTR":
			pass
		elif subchunk_name == b"SIDE":
			pass
		elif subchunk_name == b"RFOP":
			pass
		elif subchunk_name == b"RIMG":
			pass
		elif subchunk_name == b"TROP":
			pass
		elif subchunk_name == b"ALPH":
			pass
		elif subchunk_name == b"BUF1":
			pass
		elif subchunk_name == b"BUF2":
			pass
		elif subchunk_name == b"BUF3":
			pass
		elif subchunk_name == b"BUF4":
			pass
		else:
			print(f"Unimplemented SubBlock: {subchunk_name}")

		offset += subchunk_len

	lwo.surfs[surf.name] = surf


def read_surf_5(surf_bytes, lwo, dirpath=None):
	"""Read the object's surface data."""
	if len(lwo.surfs) == 0:
		print("Reading Object Surfaces 5")

	surf = _obj_surf()
	name, name_len = read_lwostring(surf_bytes)
	if len(name) != 0:
		surf.name = name

	offset = name_len
	chunk_len = len(surf_bytes)
	while offset < chunk_len:
		(subchunk_name,) = struct.unpack("4s", surf_bytes[offset : offset + 4])
		offset += 4
		(subchunk_len,) = struct.unpack(">H", surf_bytes[offset : offset + 2])
		offset += 2

		# Now test which subchunk it is.
		if subchunk_name == b"COLR":
			color = struct.unpack(">BBBB", surf_bytes[offset : offset + 4])
			surf.colr = [color[0] / 255.0, color[1] / 255.0, color[2] / 255.0]

		elif subchunk_name == b"DIFF":
			(surf.diff,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
			surf.diff /= 256.0  # Yes, 256 not 255.

		elif subchunk_name == b"LUMI":
			(surf.lumi,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
			surf.lumi /= 256.0

		elif subchunk_name == b"SPEC":
			(surf.spec,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
			surf.spec /= 256.0

		elif subchunk_name == b"REFL":
			(surf.refl,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
			surf.refl /= 256.0

		elif subchunk_name == b"TRAN":
			(surf.tran,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
			surf.tran /= 256.0

		elif subchunk_name == b"RIND":
			(surf.rind,) = struct.unpack(">f", surf_bytes[offset : offset + 4])

		elif subchunk_name == b"GLOS":
			(surf.glos,) = struct.unpack(">h", surf_bytes[offset : offset + 2])

		elif subchunk_name == b"SMAN":
			(s_angle,) = struct.unpack(">f", surf_bytes[offset : offset + 4])
			if s_angle > 0.0:
				surf.smooth = True

		elif subchunk_name in [b"CTEX", b"DTEX", b"STEX", b"RTEX", b"TTEX", b"BTEX", b"LTEX"]:
			texture = None

		elif subchunk_name == b"TIMG":
			path, path_len = read_lwostring(surf_bytes[offset:])
			if path == "(none)":
				continue

			texture = _surf_texture_5()
			lwo.clips[texture.id] = path
			surf.textures_5.append(texture)

		elif subchunk_name == b"TFLG":
			if texture:
				(mapping,) = struct.unpack(">h", surf_bytes[offset : offset + 2])
				if mapping & 1:
					texture.X = True
				elif mapping & 2:
					texture.Y = True
				elif mapping & 4:
					texture.Z = True
		elif subchunk_name == b"FLAG":
			pass  # SKIPPING
		elif subchunk_name == b"VLUM":
			pass  # SKIPPING
		elif subchunk_name == b"VDIF":
			pass  # SKIPPING
		elif subchunk_name == b"VSPC":
			pass  # SKIPPING
		elif subchunk_name == b"VRFL":
			pass  # SKIPPING
		elif subchunk_name == b"VTRN":
			pass  # SKIPPING
		elif subchunk_name == b"RFLT":
			pass  # SKIPPING
		elif subchunk_name == b"ALPH":
			pass  # SKIPPING
		else:
			print(f"Unimplemented SubBlock: {subchunk_name}")

		offset += subchunk_len

	lwo.surfs[surf.name] = surf


class lwoObject:
	def __init__(self, filename):
		self.name, self.ext = os.path.splitext(os.path.basename(filename))
		self.filename = os.path.abspath(filename)
		self.dirpath = os.path.dirname(self.filename)
		self.layers = []
		self.surfs = {}
		self.materials = {}
		self.tags = []
		self.clips = {}
		self.images = []

		self.allow_images_missing = False
		self.absfilepath = True
		self.cwd = os.getcwd()

		# self.read()

	def __eq__(self, x):
		__slots__ = (
			"layers",
			"surfs",
			"tags",
			"clips",
			"images",
		)
		for k in __slots__:
			a = getattr(self, k)
			b = getattr(x, k)
			if not a == b:
				#                 print(f"{k} mismatch:")
				#                 print(f"\t{a} != {b}")
				return False
		return True

	def read(self, ch):
		self.ch = ch

		self.f = open(self.filename, "rb")
		try:
			header, chunk_size, chunk_name = struct.unpack(">4s1L4s", self.f.read(12))
		except:
			print(f"Error parsing file header! Filename {self.filename}")
			self.f.close()
			return

		if chunk_name == b"LWO2":
			self.read_lwo2()
		elif chunk_name == b"LWOB" or chunk_name == b"LWLO":
			# LWOB and LWLO are the old format, LWLO is a layered object.
			self.read_lwob()
		else:
			self.f.close()
			msg = "Invalid LWO File Type: {}".format(self.filename)
			raise lwoUnsupportedFileException(msg)
		self.f.close()
		del self.f

	def pprint(self):

		layers = []
		for x in self.layers:
			layers.append(x.dict)
		surfs = {}
		for x in self.surfs:
			surfs[x] = self.surfs[x].dict
		d = OrderedDict()
		d["layers"] = (layers,)
		d["surfs"] = (surfs,)
		d["tags"] = (self.tags,)
		d["clips"] = (self.clips,)
		d["images"] = (self.images,)
		pprint(d)

	@property
	def search_paths(self):
		paths = [self.dirpath]
		for s in self.ch.search_paths:
			if not re.search("^/", s) and not re.search("^.:", s):
				x = os.path.join(self.dirpath, s)
				y = os.path.abspath(x)
				paths.append(y)
			else:
				paths.append(s)
		return paths
	
	def resolve_clips(self):
		files = []
		for search_path in self.search_paths:
			files.extend(glob("{0}/*.*".format(search_path)))
			if self.ch.recursive:
				files.extend(glob("{0}/**/*.*".format(search_path)))
			
		for c_id in self.clips:
			clip = self.clips[c_id]
			# LW is windows tools, so windows path need to be replaced
			# under linux, and treated the sameunder windows
			imagefile = os.path.basename(clip.replace('\\', os.sep))
			ifile = None
			for f in files:
				if re.search(re.escape(imagefile), f, re.I):
					if self.absfilepath:
						ifile = os.path.abspath(f)
					else:
						ifile = os.path.relpath(f)

					if ifile not in self.images:
						self.images.append(ifile)
					continue
			self.ch.images[c_id] = ifile

		#for c_id in self.clips:
			#if None is self.ch.images[c_id] and not self.ch.cancel_search:
				#raise lwoNoImageFoundException(
				#	"Can't find filepath for image: \"{}\"".format(self.clips[c_id])
				#)

	def validate_lwo(self):
		print(f"Validating LWO: {self.filename}")
		for surf_key in self.surfs:
			surf_data = self.surfs[surf_key]
			for textures_type in surf_data.textures.keys():
				for texture in surf_data.textures[textures_type]:
					ci = texture.clipid
					if ci not in self.clips.keys():
					#if ci not in self.ch.images.keys():
						print(f"WARNING in material {surf_data.name}")
						print(f"\tci={ci}, not present in self.clips.keys():")
						self.ch.images[ci] = None
					texture.image = self.ch.images[ci]
			for texture in surf_data.textures_5:
				ci = texture.id
				texture.image = self.ch.images[ci]

	def read_lwo2(self):
		"""Read version 2 file, LW 6+."""
		self.handle_layer = True
		self.last_pols_count = 0
		self.just_read_bones = False
		print(f"Importing LWO: {self.filename}\nLWO v2 Format")

		while True:
			try:
				rootchunk = chunk.Chunk(self.f)
			except EOFError:
				break

			if rootchunk.chunkname == b"TAGS":
				read_tags(rootchunk.read(), self)
			elif rootchunk.chunkname == b"LAYR":
				self.handle_layer = read_layr(
					rootchunk.read(), self.layers, self.ch.load_hidden
				)
			elif rootchunk.chunkname == b"PNTS" and self.handle_layer:
				read_pnts(rootchunk.read(), self.layers)
			elif rootchunk.chunkname == b"VMAP" and self.handle_layer:
				vmap_type = rootchunk.read(4)

				if vmap_type == b"WGHT":
					read_weightmap(rootchunk.read(), self.layers)
				elif vmap_type == b"MORF":
					read_morph(rootchunk.read(), self.layers, False)
				elif vmap_type == b"SPOT":
					read_morph(rootchunk.read(), self.layers, True)
				elif vmap_type == b"TXUV":
					read_uvmap(rootchunk.read(), self.layers)
				elif vmap_type == b"RGB " or vmap_type == b"RGBA":
					read_colmap(rootchunk.read(), self.layers)
				elif vmap_type == b"NORM":
					read_normmap(rootchunk.read(), self.layers)
				elif vmap_type == b"PICK":
					rootchunk.skip()  # SKIPPING
				else:
					print(f"Skipping vmap_type: {vmap_type}")
					rootchunk.skip()

			elif rootchunk.chunkname == b"VMAD" and self.handle_layer:
				vmad_type = rootchunk.read(4)

				if vmad_type == b"TXUV":
					read_uv_vmad(rootchunk.read(), self.layers, self.last_pols_count)
				elif vmad_type == b"RGB " or vmad_type == b"RGBA":
					read_color_vmad(rootchunk.read(), self.layers, self.last_pols_count)
				elif vmad_type == b"WGHT":
					# We only read the Edge Weight map if it's there.
					read_weight_vmad(rootchunk.read(), self.layers)
				elif vmad_type == b"NORM":
					read_normal_vmad(rootchunk.read(), self.layers)
				else:
					print(f"Skipping vmad_type: {vmad_type}")
					rootchunk.skip()

			elif rootchunk.chunkname == b"POLS" and self.handle_layer:
				face_type = rootchunk.read(4)
				self.just_read_bones = False
				# PTCH is LW's Subpatches, SUBD is CatmullClark.
				if (
					face_type == b"FACE" or face_type == b"PTCH" or face_type == b"SUBD"
				) and self.handle_layer:
					self.last_pols_count = read_pols(rootchunk.read(), self.layers)
					if face_type != b"FACE":
						self.layers[-1].has_subds = True
				elif face_type == b"BONE" and self.handle_layer:
					read_bones(rootchunk.read(), self)
					self.just_read_bones = True
				else:
					print(f"Skipping face_type: {face_type}")
					rootchunk.skip()

			elif rootchunk.chunkname == b"PTAG" and self.handle_layer:
				(tag_type,) = struct.unpack("4s", rootchunk.read(4))
				if tag_type == b"SURF" and not self.just_read_bones:
					# Ignore the surface data if we just read a bones chunk.
					read_surf_tags(rootchunk.read(), self.layers, self.last_pols_count)

				elif self.ch.skel_to_arm:
					if tag_type == b"BNUP":
						read_bone_tags(rootchunk.read(), self, "BNUP")
					elif tag_type == b"BONE":
						read_bone_tags(rootchunk.read(), self, "BONE")
					elif tag_type == b"PART":
						rootchunk.skip()  # SKIPPING
					elif tag_type == b"COLR":
						rootchunk.skip()  # SKIPPING
					else:
						print(f"Skipping tag: {tag_type}")
						rootchunk.skip()
				else:
					print(f"Skipping tag_type: {tag_type}")
					rootchunk.skip()
			elif rootchunk.chunkname == b"SURF":
				read_surf(rootchunk.read(), self)
			elif rootchunk.chunkname == b"CLIP":
				read_clip(rootchunk.read(), self)
			elif rootchunk.chunkname == b"BBOX":
				rootchunk.skip()  # SKIPPING
			elif rootchunk.chunkname == b"VMPA":
				rootchunk.skip()  # SKIPPING
			elif rootchunk.chunkname == b"PNTS":
				rootchunk.skip()  # SKIPPING
			elif rootchunk.chunkname == b"POLS":
				rootchunk.skip()  # SKIPPING
			elif rootchunk.chunkname == b"PTAG":
				rootchunk.skip()  # SKIPPING
			else:
				# if self.handle_layer:
				print(f"Skipping Chunk: {rootchunk.chunkname}")
				rootchunk.skip()

	def read_lwob(self):
		"""Read version 1 file, LW < 6."""
		self.last_pols_count = 0
		print(f"Importing LWO: {self.filename}\nLWO v1 Format")

		while True:
			try:
				rootchunk = chunk.Chunk(self.f)
			except EOFError:
				break

			if rootchunk.chunkname == b"SRFS":
				read_tags(rootchunk.read(), self)
			elif rootchunk.chunkname == b"LAYR":
				read_layr_5(rootchunk.read(), self.layers)
			elif rootchunk.chunkname == b"PNTS":
				if len(self.layers) == 0:
					# LWOB files have no LAYR chunk to set this up.
					nlayer = _obj_layer()
					nlayer.name = "Layer 1"
					self.layers.append(nlayer)
				read_pnts(rootchunk.read(), self.layers)
			elif rootchunk.chunkname == b"POLS":
				self.last_pols_count = read_pols_5(rootchunk.read(), self.layers)
			elif rootchunk.chunkname == b"PCHS":
				self.last_pols_count = read_pols_5(rootchunk.read(), self.layers)
				self.layers[-1].has_subds = True
			elif rootchunk.chunkname == b"PTAG":
				(tag_type,) = struct.unpack("4s", rootchunk.read(4))
				if tag_type == b"SURF":
					raise Exception("Missing commented out function")
				#                     read_surf_tags_5(
				#                         rootchunk.read(), self.layers, self.last_pols_count
				#                     )
				else:
					rootchunk.skip()
			elif rootchunk.chunkname == b"SURF":
				read_surf_5(rootchunk.read(), self)
			else:
				# For Debugging \/.
				# if handle_layer:
				print(f"Skipping Chunk: {rootchunk.chunkname}")
				rootchunk.skip()

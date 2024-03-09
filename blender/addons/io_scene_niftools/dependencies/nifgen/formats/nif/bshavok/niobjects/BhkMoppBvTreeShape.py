import logging

from nifgen.utils.mopp import getMopperCredits, getMopperOriginScaleCodeWelding
import nifgen.formats.nif as NifFormat
from nifgen.array import Array
from nifgen.formats.nif.bshavok.niobjects.BhkBvTreeShape import BhkBvTreeShape
from nifgen.formats.nif.imports import name_type_map


class BhkMoppBvTreeShape(BhkBvTreeShape):

	"""
	Bethesda extension of hkpMoppBvTreeShape. hkpMoppBvTreeShape is a bounding volume tree using Havok-proprietary MOPP code.
	"""

	__name__ = 'bhkMoppBvTreeShape'


	@classmethod
	def _get_attribute_list(cls):
		yield from super()._get_attribute_list()
		yield 'unused_01', Array, (0, None, (12,), name_type_map['Byte']), (False, None), (None, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0), (None, None)
		yield 'mopp_code', name_type_map['HkpMoppCode'], (0, None), (False, None), (None, None)

	@classmethod
	def _get_filtered_attribute_list(cls, instance, include_abstract=True):
		yield from super()._get_filtered_attribute_list(instance, include_abstract)
		yield 'unused_01', Array, (0, None, (12,), name_type_map['Byte']), (False, None)
		yield 'scale', name_type_map['Float'], (0, None), (False, 1.0)
		yield 'mopp_code', name_type_map['HkpMoppCode'], (0, None), (False, None)

	def get_mass_center_inertia(self, density=1, solid=True):
		"""Return mass, center of gravity, and inertia tensor."""
		return self.get_shape_mass_center_inertia(
			density=density, solid=solid)

	def update_origin_scale(self):
		"""Update scale and origin."""
		minx = min(v.x for v in self.shape.data.vertices)
		miny = min(v.y for v in self.shape.data.vertices)
		minz = min(v.z for v in self.shape.data.vertices)
		maxx = max(v.x for v in self.shape.data.vertices)
		maxy = max(v.y for v in self.shape.data.vertices)
		maxz = max(v.z for v in self.shape.data.vertices)
		radius = self.shape.radius
		origin_scale = self.mopp_code.offset
		origin_scale.x = minx - radius
		origin_scale.y = miny - radius
		origin_scale.z = minz - radius
		origin_scale.w = (256*256*254) / ((2 * radius) + max([maxx - minx, maxy - miny, maxz - minz]))

	def update_mopp(self):
		"""Update the MOPP data, scale, and origin, and welding info.

		@deprecated: use update_mopp_welding instead
		"""
		self.update_mopp_welding()

	def update_mopp_welding(self):
		"""Update the MOPP data, scale, and origin, and welding info."""
		logger = logging.getLogger("generated.formats.nif.mopp")
		# check type of shape
		if not isinstance(self.shape, NifFormat.classes.BhkPackedNiTriStripsShape):
			raise ValueError(
				"expected bhkPackedNiTriStripsShape on mopp"
				" but got %s instead" % self.shape.__class__.__name__)
		# first try with generated.utils.mopp
		failed = False
		try:
			print(getMopperCredits())
		except (OSError, RuntimeError):
			failed = True
		else:
			# find material indices per triangle
			material_per_vertex = []
			for subshape in self.shape.get_sub_shapes():
				material_per_vertex += (
					[subshape.material] * subshape.num_vertices)
			material_per_triangle = [
				material_per_vertex[hktri.triangle.v_1]
				for hktri in self.shape.data.triangles]
			# compute havok info
			try:
				origin, scale, mopp, welding_infos \
				= getMopperOriginScaleCodeWelding(
					[vert.as_tuple() for vert in self.shape.data.vertices],
					[(hktri.triangle.v_1,
					  hktri.triangle.v_2,
					  hktri.triangle.v_3)
					 for hktri in self.shape.data.triangles],
					material_per_triangle)
			except (OSError, RuntimeError):
				failed = True
			else:
				# must use calculated scale and origin
				origin_scale = self.mopp_code.offset
				origin_scale.w = scale
				origin_scale.x = origin[0]
				origin_scale.y = origin[1]
				origin_scale.z = origin[2]
		# if havok's mopper failed, do a simple mopp
		if failed:
			logger.exception(
				"Havok mopp generator failed, falling back on simple mopp "
				"(but collisions may be flawed in-game!)."
				"If you are using the PyFFI that was shipped with Blender, "
				"and you are on Windows, then you may wish to install the "
				"full version of PyFFI from "
				"https://github.com/niftools/pyffi "
				"instead, which includes the (closed source) "
				"Havok mopp generator.")
			self.update_origin_scale()
			mopp = self._makeSimpleMopp()
			# no welding info
			welding_infos = []

		# delete mopp and replace with new data
		self.mopp_code.data_size = len(mopp)
		self.mopp_code.reset_field("data")
		data = self.mopp_code.data
		for i, b in enumerate(mopp):
			data[i] = b

		# update welding information
		for hktri, welding_info in zip(self.shape.data.triangles, welding_infos):
			hktri.welding_info = welding_info

	def _makeSimpleMopp(self):
		"""Make a simple mopp."""
		mopp = [] # the mopp 'assembly' script
		self._q = 256*256 / self.scale # quantization factor

		# opcodes
		BOUNDX = 0x26
		BOUNDY = 0x27
		BOUNDZ = 0x28
		TESTX = 0x10
		TESTY = 0x11
		TESTZ = 0x12

		# add first crude bounding box checks
		self._vertsceil  = [ self._moppCeil(v) for v in self.shape.data.vertices ]
		self._vertsfloor = [ self._moppFloor(v) for v in self.shape.data.vertices ]
		minx = min([ v[0] for v in self._vertsfloor ])
		miny = min([ v[1] for v in self._vertsfloor ])
		minz = min([ v[2] for v in self._vertsfloor ])
		maxx = max([ v[0] for v in self._vertsceil ])
		maxy = max([ v[1] for v in self._vertsceil ])
		maxz = max([ v[2] for v in self._vertsceil ])
		if minx < 0 or miny < 0 or minz < 0: raise ValueError("cannot update mopp tree with invalid origin")
		if maxx > 255 or maxy > 255 or maxz > 255: raise ValueError("cannot update mopp tree with invalid scale")
		mopp.extend([BOUNDZ, minz, maxz])
		mopp.extend([BOUNDY, miny, maxy])
		mopp.extend([BOUNDX, minx, maxx])

		# add tree using subsequent X-Y-Z splits
		# (slow and no noticable difference from other simple tree so deactivated)
		#tris = range(len(self.shape.data.triangles))
		#tree = self.split_triangles(tris, [[minx,maxx],[miny,maxy],[minz,maxz]])
		#mopp += self.mopp_from_tree(tree)

		# add a trivial tree
		# this prevents the player of walking through the model
		# but arrows may still fly through
		numtriangles = len(self.shape.data.triangles)
		i = 0x30
		for t in range(numtriangles-1):
			 mopp.extend([TESTZ, maxz, 0, 1, i])
			 i += 1
			 if i == 0x50:
				 mopp.extend([0x09, 0x20]) # increment triangle offset
				 i = 0x30
		mopp.extend([i])

		return mopp

	def _moppCeil(self, v):
		origin_scale = self.mopp_code.offset
		radius = self.shape.radius
		moppx = int((v.x + radius - origin_scale.x) / self._q + 0.99999999)
		moppy = int((v.y + radius - origin_scale.y) / self._q + 0.99999999)
		moppz = int((v.z + radius - origin_scale.z) / self._q + 0.99999999)
		return [moppx, moppy, moppz]

	def _moppFloor(self, v):
		origin_scale = self.mopp_code.offset
		radius = self.shape.radius
		moppx = int((v.x - radius - origin_scale.x) / self._q)
		moppy = int((v.y - radius - origin_scale.y) / self._q)
		moppz = int((v.z - radius - origin_scale.z) / self._q)
		return [moppx, moppy, moppz]

	def split_triangles(self, ts, bbox, dir=0):
		"""Direction 0=X, 1=Y, 2=Z"""
		btest = [] # for bounding box tests
		test = [] # for branch command
		# check bounding box
		tris = [ t.triangle for t in self.shape.data.triangles ]
		tsverts = [ tris[t].v_1 for t in ts] + [ tris[t].v_2 for t in ts] + [ tris[t].v_3 for t in ts]
		minx = min([self._vertsfloor[v][0] for v in tsverts])
		miny = min([self._vertsfloor[v][1] for v in tsverts])
		minz = min([self._vertsfloor[v][2] for v in tsverts])
		maxx = max([self._vertsceil[v][0] for v in tsverts])
		maxy = max([self._vertsceil[v][1] for v in tsverts])
		maxz = max([self._vertsceil[v][2] for v in tsverts])
		# add bounding box checks if it's reduced in a direction
		if (maxx - minx < bbox[0][1] - bbox[0][0]):
			btest += [ 0x26, minx, maxx ]
			bbox[0][0] = minx
			bbox[0][1] = maxx
		if (maxy - miny < bbox[1][1] - bbox[1][0]):
			btest += [ 0x27, miny, maxy ]
			bbox[1][0] = miny
			bbox[1][1] = maxy
		if (maxz - minz < bbox[2][1] - bbox[2][0]):
			btest += [ 0x28, minz, maxz ]
			bbox[2][0] = minz
			bbox[2][1] = maxz
		# if only one triangle, no further split needed
		if len(ts) == 1:
			if ts[0] < 32:
				return [ btest, [ 0x30 + ts[0] ], [], [] ]
			elif ts[0] < 256:
				return [ btest, [ 0x50, ts[0] ], [], [] ]
			else:
				return [ btest, [ 0x51, ts[0] >> 8, ts[0] & 255 ], [], [] ]
		# sort triangles in required direction
		ts.sort(key = lambda t: max(self._vertsceil[tris[t].v_1][dir], self._vertsceil[tris[t].v_2][dir], self._vertsceil[tris[t].v_3][dir]))
		# split into two
		ts1 = ts[:len(ts)/2]
		ts2 = ts[len(ts)/2:]
		# get maximum coordinate of small group
		ts1verts = [ tris[t].v_1 for t in ts1] + [ tris[t].v_2 for t in ts1] + [ tris[t].v_3 for t in ts1]
		ts2verts = [ tris[t].v_1 for t in ts2] + [ tris[t].v_2 for t in ts2] + [ tris[t].v_3 for t in ts2]
		ts1max = max([self._vertsceil[v][dir] for v in ts1verts])
		# get minimum coordinate of large group
		ts2min = min([self._vertsfloor[v][dir] for v in ts2verts])
		# set up test
		test += [0x10+dir, ts1max, ts2min]
		# set up new bounding boxes for each subtree
		# make copy
		bbox1 = [[bbox[0][0],bbox[0][1]],[bbox[1][0],bbox[1][1]],[bbox[2][0],bbox[2][1]]]
		bbox2 = [[bbox[0][0],bbox[0][1]],[bbox[1][0],bbox[1][1]],[bbox[2][0],bbox[2][1]]]
		# update bound in test direction
		bbox1[dir][1] = ts1max
		bbox2[dir][0] = ts2min
		# return result
		nextdir = dir+1
		if nextdir == 3: nextdir = 0
		return [btest, test, self.split_triangles(ts1, bbox1, nextdir), self.split_triangles(ts2, bbox2, nextdir)]

	def mopp_from_tree(self, tree):
		if tree[1][0] in range(0x30, 0x52):
			return tree[0] + tree[1]
		mopp = tree[0] + tree[1]
		submopp1 = self.mopp_from_tree(tree[2])
		submopp2 = self.mopp_from_tree(tree[3])
		if len(submopp1) < 256:
			mopp += [ len(submopp1) ]
			mopp += submopp1
			mopp += submopp2
		else:
			jump = len(submopp2)
			if jump <= 255:
				mopp += [2, 0x05, jump]
			else:
				mopp += [3, 0x06, jump >> 8, jump & 255]
			mopp += submopp2
			mopp += submopp1
		return mopp

	# ported and extended from NifVis/bhkMoppBvTreeShape.py
	def parse_mopp(self, start = 0, depth = 0, toffset = 0, verbose = False):
		"""The mopp data is printed to the debug channel
		while parsed. Returns list of indices into mopp data of the bytes
		processed and a list of triangle indices encountered.

		The verbose argument is ignored (and is deprecated).
		"""
		class Message:
			def __init__(self):
				self.logger = logging.getLogger("generated.formats.nif.mopp")
				self.msg = ""

			def append(self, *args):
				self.msg += " ".join(str(arg) for arg in args) + " "
				return self

			def debug(self):
				if self.msg:
					self.logger.debug(self.msg)
					self.msg = ""

			def error(self):
				self.logger.error(self.msg)
				self.msg = ""

		mopp = self.mopp_code.data # shortcut notation
		ids = [] # indices of bytes processed
		tris = [] # triangle indices
		i = start # current index
		ret = False # set to True if an opcode signals a triangle index
		while i < self.mopp_code.data_size and not ret:
			# get opcode and print it
			code = mopp[i]
			msg = Message()
			msg.append("%4i:"%i + "  "*depth + '0x%02X ' % code)

			if code == 0x09:
				# increment triangle offset
				toffset += mopp[i+1]
				msg.append(mopp[i+1])
				msg.append('%i [ triangle offset += %i, offset is now %i ]'
								% (mopp[i+1], mopp[i+1], toffset))
				ids.extend([i,i+1])
				i += 2

			elif code in [ 0x0A ]:
				# increment triangle offset
				toffset += mopp[i+1]*256 + mopp[i+2]
				msg.append(mopp[i+1],mopp[i+2])
				msg.append('[ triangle offset += %i, offset is now %i ]'
								% (mopp[i+1]*256 + mopp[i+2], toffset))
				ids.extend([i,i+1,i+2])
				i += 3

			elif code in [ 0x0B ]:
				# unsure about first two arguments, but the 3rd and 4th set triangle offset
				toffset = 256*mopp[i+3] + mopp[i+4]
				msg.append(mopp[i+1],mopp[i+2],mopp[i+3],mopp[i+4])
				msg.append('[ triangle offset = %i ]' % toffset)
				ids.extend([i,i+1,i+2,i+3,i+4])
				i += 5

			elif code in range(0x30,0x50):
				# triangle compact
				msg.append('[ triangle %i ]'%(code-0x30+toffset))
				ids.append(i)
				tris.append(code-0x30+toffset)
				i += 1
				ret = True

			elif code == 0x50:
				# triangle byte
				msg.append(mopp[i+1])
				msg.append('[ triangle %i ]'%(mopp[i+1]+toffset))
				ids.extend([i,i+1])
				tris.append(mopp[i+1]+toffset)
				i += 2
				ret = True

			elif code in [ 0x51 ]:
				# triangle short
				t = mopp[i+1]*256 + mopp[i+2] + toffset
				msg.append(mopp[i+1],mopp[i+2])
				msg.append('[ triangle %i ]' % t)
				ids.extend([i,i+1,i+2])
				tris.append(t)
				i += 3
				ret = True

			elif code in [ 0x53 ]:
				# triangle short?
				t = mopp[i+3]*256 + mopp[i+4] + toffset
				msg.append(mopp[i+1],mopp[i+2],mopp[i+3],mopp[i+4])
				msg.append('[ triangle %i ]' % t)
				ids.extend([i,i+1,i+2,i+3,i+4])
				tris.append(t)
				i += 5
				ret = True

			elif code in [ 0x05 ]:
				# byte jump
				msg.append('[ jump -> %i: ]'%(i+2+mopp[i+1]))
				ids.extend([i,i+1])
				i += 2+mopp[i+1]

			elif code in [ 0x06 ]:
				# short jump
				jump = mopp[i+1]*256 + mopp[i+2]
				msg.append('[ jump -> %i: ]'%(i+3+jump))
				ids.extend([i,i+1,i+2])
				i += 3+jump

			elif code in [0x10,0x11,0x12, 0x13,0x14,0x15, 0x16,0x17,0x18, 0x19, 0x1A, 0x1B, 0x1C]:
				# compact if-then-else with two arguments
				msg.append(mopp[i+1], mopp[i+2])
				if code == 0x10:
					msg.append('[ branch X')
				elif code == 0x11:
					msg.append('[ branch Y')
				elif code == 0x12:
					msg.append('[ branch Z')
				else:
					msg.append('[ branch ?')
				msg.append('-> %i: %i: ]'%(i+4,i+4+mopp[i+3]))
				msg.debug()
				msg.append("	 " + "  "*depth + 'if:')
				msg.debug()
				idssub1, trissub1 = self.parse_mopp(start = i+4, depth = depth+1, toffset = toffset, verbose = verbose)
				msg.append("	 " + "  "*depth + 'else:')
				msg.debug()
				idssub2, trissub2 = self.parse_mopp(start = i+4+mopp[i+3], depth = depth+1, toffset = toffset, verbose = verbose)
				ids.extend([i,i+1,i+2,i+3])
				ids.extend(idssub1)
				ids.extend(idssub2)
				tris.extend(trissub1)
				tris.extend(trissub2)
				ret = True

			elif code in [0x20,0x21,0x22]:
				# compact if-then-else with one argument
				msg.append(mopp[i+1], '[ branch ? -> %i: %i: ]'%(i+3,i+3+mopp[i+2])).debug()
				msg.append("	 " + "  "*depth + 'if:').debug()
				idssub1, trissub1 = self.parse_mopp(start = i+3, depth = depth+1, toffset = toffset, verbose = verbose)
				msg.append("	 " + "  "*depth + 'else:').debug()
				idssub2, trissub2 = self.parse_mopp(start = i+3+mopp[i+2], depth = depth+1, toffset = toffset, verbose = verbose)
				ids.extend([i,i+1,i+2])
				ids.extend(idssub1)
				ids.extend(idssub2)
				tris.extend(trissub1)
				tris.extend(trissub2)
				ret = True

			elif code in [0x23,0x24,0x25]: # short if x <= a then 1; if x > b then 2;
				jump1 = mopp[i+3] * 256 + mopp[i+4]
				jump2 = mopp[i+5] * 256 + mopp[i+6]
				msg.append(mopp[i+1], mopp[i+2], '[ branch ? -> %i: %i: ]'%(i+7+jump1,i+7+jump2)).debug()
				msg.append("	 " + "  "*depth + 'if:').debug()
				idssub1, trissub1 = self.parse_mopp(start = i+7+jump1, depth = depth+1, toffset = toffset, verbose = verbose)
				msg.append("	 " + "  "*depth + 'else:').debug()
				idssub2, trissub2 = self.parse_mopp(start = i+7+jump2, depth = depth+1, toffset = toffset, verbose = verbose)
				ids.extend([i,i+1,i+2,i+3,i+4,i+5,i+6])
				ids.extend(idssub1)
				ids.extend(idssub2)
				tris.extend(trissub1)
				tris.extend(trissub2)
				ret = True
			elif code in [0x26,0x27,0x28]:
				msg.append(mopp[i+1], mopp[i+2])
				if code == 0x26:
					msg.append('[ bound X ]')
				elif code == 0x27:
					msg.append('[ bound Y ]')
				elif code == 0x28:
					msg.append('[ bound Z ]')
				ids.extend([i,i+1,i+2])
				i += 3
			elif code in [0x01, 0x02, 0x03, 0x04]:
				msg.append(mopp[i+1], mopp[i+2], mopp[i+3], '[ bound XYZ? ]')
				ids.extend([i,i+1,i+2,i+3])
				i += 4
			else:
				msg.append("unknown mopp code 0x%02X"%code).error()
				msg.append("following bytes are").debug()
				extrabytes = [mopp[j] for j in range(i+1,min(self.mopp_code.data_size,i+10))]
				extraindex = [j	for j in range(i+1,min(self.mopp_code.data_size,i+10))]
				msg.append(extrabytes).debug()
				for b, j in zip(extrabytes, extraindex):
					if j+b+1 < self.mopp_data_size:
						msg.append("opcode after jump %i is 0x%02X"%(b,mopp[j+b+1]), [mopp[k] for k in range(j+b+2,min(self.mopp_data_size,j+b+11))]).debug()
				raise ValueError("unknown mopp opcode 0x%02X"%code)

			msg.debug()

		return ids, tris


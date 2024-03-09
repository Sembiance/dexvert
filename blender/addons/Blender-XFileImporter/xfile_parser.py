from __future__ import annotations

import codecs
import struct
from warnings import *
from .xfile_helper import *
import array
import zlib

MSZIP_MAGIC = 0x4B43
MSZIP_BLOCK = 32786


class XFileParser(object):
	"""The XFileParser reads a XFile either in text or binary form and builds a temporary
	data structure out of it.

	Attributes:
		majorVersion: version numbers
		minorVersion: version numbers
		isBinaryFormat: true if the file is in binary, false if it's in text form
		binaryFloatSize: float size, either 32 or 64 bits
		binaryNumCount: counter for number arrays in binary format
		lineNumber: Line number when reading in text format
		scene: Imported data
	"""
	majorVersion: int
	minorVersion: int
	isBinaryFormat: bool
	binaryFloatSize: int
	binaryNumCount: int
	p: int
	end: int
	buffer: bytes
	lineNumber: int
	scene: Scene

	def __init__(self, buffer: bytes):
		""" Constructor. Creates a data structure out of the XFile given in the memory block. 
		Args:
			pBuffer: Null-terminated memory buffer containing the XFile
		"""
		self.majorVersion = 0
		self.minorVersion = 0
		self.isBinaryFormat = False
		self.binaryFloatSize = 0
		self.binaryNumCount = 0
		self.p = -1
		self.end = -1
		self.buffer = buffer
		self.lineNumber = 0
		self.scene = None

		# set up memory pointers
		self.p = 0
		self.end = buffer.__len__()

		# check header
		if self.buffer[self.p:self.p+4] != b'xof ':
			self.ThrowException('Header mismatch, file is not an XFile.')

		# read version. It comes in a four byte format such as "0302"
		self.majorVersion = int(self.buffer[4:4+2])
		self.minorVersion = int(self.buffer[6:6+2])

		compressed = False

		# txt - pure ASCII text format
		if (self.buffer[8:12] == b'txt '):
			self.isBinaryFormat = False
		elif(self.buffer[8:12] == b'bin '):
			self.isBinaryFormat = True
		elif(self.buffer[8:12] == b'tzip'):
			self.isBinaryFormat = False
			compressed = True
		elif(self.buffer[8:12] == b'bzip'):
			self.isBinaryFormat = True
			compressed = True
		else:
			self.ThrowException('Unsupported xfile format ' +
								self.buffer[8:12].deocde())
		# float size
		self.binaryFloatSize = int(self.buffer[12:16])

		if self.binaryFloatSize != 32 and self.binaryFloatSize != 64:
			self.ThrowException(
				'Unknown float size %d specified in xfile header.' % self.binaryFloatSize)

		self.p += 16

		# If this is a compressed X file, apply the inflate algorithm to it
		if compressed:
			self.p += 6
			p1 = self.p
			est_out = 0
			while p1 + 3 < self.end:
				# read next offset
				ofs = struct.unpack_from('H', self.buffer, p1)[0]
				p1 += 2
				if ofs >= MSZIP_BLOCK:
					raise Exception(
						"X: Invalid offset to next MSZIP compressed block")
				# check magic word
				magic = struct.unpack_from('H', self.buffer, p1)[0]
				p1 += 2
				if magic != MSZIP_MAGIC:
					raise Exception(
						"X: Unsupported compressed format, expected MSZIP header")

				# and advance to the next offset
				p1 += ofs
				est_out += MSZIP_BLOCK

			# Allocate storage and terminating zero and do the actual uncompressing
			uncompressedEnd = 0
			while self.p + 3 < self.end:
				ofs = struct.unpack_from('H', self.buffer, self.p)[0]
				self.p += 4
				if self.p + ofs > self.end + 2:
					raise Exception("X: Unexpected EOF in compressed chunk")
				uncompressed = zlib.decompress(
					self.buffer[self.p:], -8, MSZIP_BLOCK)
				uncompressedEnd += len(uncompressed)
				self.p += ofs
			self.buffer = uncompressed
			self.end = uncompressedEnd
			self.p = 0
		else:
			self.ReadUntilEndOfLine()

		self.scene = Scene()
		self.ParseFile()

		# filter the imported hierarchy for some degenerated cases
		if self.scene.rootNode:
			self.FilterHierarchy(self.scene.rootNode)

	def __del__(self):
		""" Destructor. Destroys all imported data along with it """

	def getImportedData(self) -> Scene:
		return self.scene

	def ParseFile(self):
		running = True
		while(running):
			objectName = self.GetNextToken()
			if not objectName:
				break
			if objectName == b'template':
				self.ParseDataObjectTemplate()
			elif objectName == b'Frame':
				self.ParseDataObjectFrame()
			elif objectName == b'Mesh':
				mesh = self.ParseDataObjectMesh()
				self.scene.globalMeshes.append(mesh)
			elif objectName == b'AnimTicksPerSecond':
				self.ParseDataObjectAnimTicksPerSecond()
			elif objectName == b'AnimationSet':
				self.ParseDataObjectAnimationSet()
			elif objectName == b'Material':
				material = self.ParseDataObjectMaterial()
				self.scene.globalMaterials.append(material)
			elif objectName == b'}':
				warn("} found in dataObject")
			else:
				#warn("Unknown data object in animation of .x file")
				self.ParseUnknownDataObject()

	def ParseDataObjectTemplate(self):
		name = self.ReadHeadOfDataObject()
		guid = self.GetNextToken()
		running = True
		while(running):
			s = self.GetNextToken()
			if (s == b'}'):
				break
			if not s:
				self.ThrowException(
					"Unexpected end of file reached while parsing template definition")

	def ParseDataObjectFrame(self, parent: Node | None = None):
		name = self.ReadHeadOfDataObject()
		node = Node(parent)
		node.name = name.decode()
		if parent:
			parent.children.append(node)
		else:
			if self.scene.rootNode:
				if self.scene.rootNode.name != '$dummy_root':
					exroot = self.scene.rootNode
					self.scene.rootNode = Node()
					self.scene.rootNode.children.append(exroot)
					exroot.parent = self.scene.rootNode
				self.scene.rootNode.children.append(node)
				node.parent = self.scene.rootNode
			else:
				self.scene.rootNode = node

		running = True
		while running:
			objectName = self.GetNextToken()
			if not objectName:
				self.ThrowException(
					"Unexpected end of file reached while parsing frame")
			if objectName == b'}':
				break
			elif objectName == b'Frame':
				self.ParseDataObjectFrame(node)
			elif objectName == b'FrameTransformMatrix':
				node.trafoMatrix = self.ParseDataObjectTransformationMatrix()
			elif objectName == b'Mesh':
				mesh = self.ParseDataObjectMesh()
				node.meshes.append(mesh)
			else:
				warn("Unknown data object in frame in x file")
				self.ParseUnknownDataObject()

	def ParseDataObjectTransformationMatrix(self) -> tuple[float, ...]:
		# read header, we're not interested if it has a name
		self.ReadHeadOfDataObject()

		# read its components
		M11 = self.ReadFloat()
		M21 = self.ReadFloat()
		M31 = self.ReadFloat()
		M41 = self.ReadFloat()
		M12 = self.ReadFloat()
		M22 = self.ReadFloat()
		M32 = self.ReadFloat()
		M42 = self.ReadFloat()
		M13 = self.ReadFloat()
		M23 = self.ReadFloat()
		M33 = self.ReadFloat()
		M43 = self.ReadFloat()
		M14 = self.ReadFloat()
		M24 = self.ReadFloat()
		M34 = self.ReadFloat()
		M44 = self.ReadFloat()

		# trailing symbols
		self.CheckForSemicolon()
		self.CheckForClosingBrace()

		return (M11, M21, M31, M41, M12, M22, M32, M42, M13, M23, M33, M43, M14, M24, M34, M44)

	def ParseDataObjectMesh(self) -> Mesh:
		mesh = Mesh()
		name = self.ReadHeadOfDataObject()

		# read veretx count
		numVertices = self.ReadInt()

		# read vertices
		for a in range(numVertices):
			mesh.positions.append(self.ReadVector3())

		# read position faces
		numPosFaces = self.ReadInt()
		mesh.posFaces = []
		for a in range(numPosFaces):
			numIndices = self.ReadInt()
			if numIndices < 3:
				self.ThrowException(
					"Invalid index count %1% for face %2%.".format(numIndices, a))
			# read indices
			face = Face()
			face.indices = []
			for b in range(numIndices):
				face.indices.append(self.ReadInt())
			mesh.posFaces.append(face)
			self.TestForSeparator()

		# here, other data objects may follow
		running = True
		while running:
			objectName = self.GetNextToken()

			if not objectName:
				self.ThrowException(
					"Unexpected end of file while parsing mesh structure")
			elif objectName == b'}':
				break  # mesh finished
			elif objectName == b'MeshNormals':
				self.ParseDataObjectMeshNormals(mesh)
			elif objectName == b'MeshTextureCoords':
				self.ParseDataObjectMeshTextureCoords(mesh)
			elif objectName == b'MeshVertexColors':
				self.ParseDataObjectMeshVertexColors(mesh)
			elif objectName == b'MeshMaterialList':
				self.ParseDataObjectMeshMaterialList(mesh)
			elif objectName == b'VertexDuplicationIndices':
				self.ParseUnknownDataObject()  # we'll ignore vertex duplication indices
			elif objectName == b'XSkinMeshHeader':
				self.ParseDataObjectSkinMeshHeader(mesh)
			elif objectName == b'SkinWeights':
				self.ParseDataObjectSkinWeights(mesh)
			else:
				print("Unknown data object in mesh in x file")
				self.ParseUnknownDataObject()

		return mesh

	def ParseDataObjectSkinWeights(self, mesh: Mesh):
		if not mesh:
			return

		self.ReadHeadOfDataObject()

		transformNodeName = self.GetNextTokenAsString()

		mesh.bones.append(Bone())
		bone = mesh.bones[len(mesh.bones)-1]
		bone.name = transformNodeName.decode()

		# read vertex weights
		numWeights = self.ReadInt()
		bone.weights = []

		for a in range(0, numWeights):
			weight = BoneWeight()
			weight.vertex = self.ReadInt()
			bone.weights.append(weight)

		# read vertex weights
		for a in range(0, numWeights):
			bone.weights[a].weight = self.ReadFloat()

		# read matrix offset
		a1 = self.ReadFloat()
		b1 = self.ReadFloat()
		c1 = self.ReadFloat()
		d1 = self.ReadFloat()
		a2 = self.ReadFloat()
		b2 = self.ReadFloat()
		c2 = self.ReadFloat()
		d2 = self.ReadFloat()
		a3 = self.ReadFloat()
		b3 = self.ReadFloat()
		c3 = self.ReadFloat()
		d3 = self.ReadFloat()
		a4 = self.ReadFloat()
		b4 = self.ReadFloat()
		c4 = self.ReadFloat()
		d4 = self.ReadFloat()
		bone.offsetMatrix = (a1, b1, c1, d1, a2, b2, c2,
							 d2, a3, b3, c3, d3, a4, b4, c4, d4)

		self.CheckForSemicolon()
		self.CheckForClosingBrace()

	def ParseDataObjectSkinMeshHeader(self, mesh: Mesh):
		self.ReadHeadOfDataObject()

		self.ReadInt()  # maxSkinWeightsPerVertex
		self.ReadInt()  # maxSkinWeightsPerFace
		self.ReadInt()  # numBonesInMesh

		self.CheckForClosingBrace()

	def ParseDataObjectMeshNormals(self, mesh: Mesh):
		self.ReadHeadOfDataObject()

		# read count
		numNormals = self.ReadInt()

		# read normal vectors
		for a in range(numNormals):
			mesh.normals.append(self.ReadVector3())

		# read normal indices
		numFaces = self.ReadInt()
		if numFaces != len(mesh.posFaces):
			self.ThrowException(
				"Normal face count does not match vertex face count.")

		for a in range(0, numFaces):
			numIndices = self.ReadInt()
			face = Face()
			face.indices = []
			for b in range(0, numIndices):
				face.indices.append(self.ReadInt())
			mesh.normalFaces.append(face)
			self.TestForSeparator()

		self.CheckForClosingBrace()

	def ParseDataObjectMeshTextureCoords(self, mesh: Mesh):
		self.ReadHeadOfDataObject()
		if mesh.numTextures + 1 > AI_MAX_NUMBER_OF_TEXTURECOORDS:
			self.ThrowException("Too many sets of texture coordinates")

		numCoords = self.ReadInt()
		if numCoords != len(mesh.positions):
			self.ThrowException(
				"Texture coord count does not match vertex count")

		coords = [0]*numCoords
		for a in range(numCoords):
			coords[a] = self.ReadVector2()

		mesh.texCoords = coords
		mesh.numTextures += 1

		self.CheckForClosingBrace()

	def ParseDataObjectMeshVertexColors(self, mesh: Mesh):
		self.ReadHeadOfDataObject()
		if mesh.numColorSets+1 > AI_MAX_NUMBER_OF_COLOR_SETS:
			self.ThrowException("Too many colorsets")
		colors = mesh.colors[mesh.numColorSets]
		mesh.numColorSets += 1

		numColors = self.ReadInt()
		if numColors != len(mesh.positions):
			self.ThrowException(
				"Vertex color count does not match vertex count")

		colors.extend([(0.0, 0.0, 0.0, 1.0)]*numColors)
		for a in range(numColors):
			index = self.ReadInt()
			if index >= len(mesh.positions):
				self.ThrowException("Vertex color index out of bounds")

			colors[index] = self.ReadRGBA()
			# HACK: (thom) Maxon Cinema XPort plugin puts a third separator here, kwxPort puts a comma.
			# Ignore gracefully.
			if not self.isBinaryFormat:
				if self.buffer[self.p:self.p+1] == b';' or self.buffer[self.p:self.p+1] == b',':
					self.p += 1

		self.CheckForClosingBrace()

	def ParseDataObjectMeshMaterialList(self, mesh: Mesh):
		self.ReadHeadOfDataObject()

		# read material count
		# unsigned int numMaterials =
		self.ReadInt()
		# read non triangulated face material index count
		numMatIndices = self.ReadInt()

		if numMatIndices != len(mesh.posFaces) and numMatIndices != 1:
			self.ThrowException(
				"Per-Face material index count does not match face count.")

		# read per-face material indices
		for a in range(numMatIndices):
			mesh.faceMaterials.append(self.ReadInt())

		# in version 03.02, the face indices end with two semicolons.
		# commented out version check, as version 03.03 exported from blender also has 2 semicolons
		if not self.isBinaryFormat:  # && MajorVersion == 3 && MinorVersion <= 2)
			if self.p < self.end and self.buffer[self.p:self.p+1] == b';':
				self.p += 1

		# if there was only a single material index, replicate it on all faces
		while len(mesh.faceMaterials) < len(mesh.posFaces):
			mesh.faceMaterials.append(mesh.faceMaterials[0])

		# read following data objects
		running = True
		while running:
			objectName = self.GetNextToken()
			if len(objectName) == 0:
				self.ThrowException(
					"Unexpected end of file while parsing mesh material list.")
			elif objectName == b'}':
				break  # material list finished
			elif objectName == b'{':
				matName = self.GetNextToken()
				material = Material()
				material.isReference = True
				material.name = matName.decode()
				mesh.materials.append(material)

				self.CheckForClosingBrace()
			elif objectName == b'Material':
				material = self.ParseDataObjectMaterial()
				mesh.materials.append(material)
			elif objectName == b';':
				pass
				# ignore
			else:
				warn("Unknown data object in material list in x file")
				self.ParseUnknownDataObject()

	def ParseDataObjectMaterial(self) -> Material:
		material = Material()

		matName = self.ReadHeadOfDataObject()
		if not matName:
			matName = b'material'+(str(self.lineNumber)).encode('ascii')
		material.name = matName.decode()
		material.isReference = False

		# read material values
		material.diffuse = self.ReadRGBA()
		material.specularExponent = self.ReadFloat()
		material.specular = self.ReadRGB()
		material.emissive = self.ReadRGB()

		# read other data objects
		running = True
		while running:
			objectName = self.GetNextToken()
			if not objectName:
				self.ThrowException(
					"Unexpected end of file while parsing mesh material")
			elif objectName == b'}':
				break  # material finished
			elif objectName == b'TextureFilename' or objectName == b'TextureFileName':
				# some exporters write "TextureFileName" instead.
				texname = self.ParseDataObjectTextureFilename()
				material.textures.append(TexEntry(texname))
			elif objectName == b'NormalmapFilename' or objectName == b'NormalmapFileName':
				# one exporter writes out the normal map in a separate filename tag
				texname = self.ParseDataObjectTextureFilename()
				material.textures.append(TexEntry(texname, True))
			else:
				warn("Unknown data object in material in x file")
				self.ParseUnknownDataObject()

		return material

	def ParseDataObjectAnimTicksPerSecond(self):
		self.ReadHeadOfDataObject()
		self.scene.AnimTicksPerSecond = self.ReadInt()
		self.CheckForClosingBrace()

	def ParseDataObjectAnimationSet(self):
		animName = self.ReadHeadOfDataObject()

		anim = Animation()
		self.scene.anims.append(anim)
		anim.name = animName.decode()

		running = True
		while running:
			objectName = self.GetNextToken()
			if not objectName:
				self.ThrowException(
					"Unexpected end of file while parsing animation set.")
			elif objectName == b'}':
				break  # animation set finished
			elif objectName == b'Animation':
				self.ParseDataObjectAnimation(anim)
			else:
				warn('Unknown data object in animation set in x file')
				self.ParseUnknownDataObject()

	def ParseDataObjectAnimation(self, anim: Animation):
		self.ReadHeadOfDataObject()
		banim = AnimBone()
		anim.anims.append(banim)

		running = True
		while running:
			objectName = self.GetNextToken()

			if not objectName:
				self.ThrowException(
					"Unexpected end of file while parsing animation.")
			elif objectName == b'}':
				break
			elif objectName == b'AnimationKey':
				self.ParseDataObjectAnimationKey(banim)
			elif objectName == b'AnimationOptions':
				self.ParseUnknownDataObject()
			elif objectName == b'{':
				banim.boneName = self.GetNextToken()
				self.CheckForClosingBrace()
			else:
				warn("Unknown data object in animation in x file")
				self.ParseUnknownDataObject()

	def ParseDataObjectAnimationKey(self, animBone: AnimBone):
		self.ReadHeadOfDataObject()

		# read key type
		keyType = self.ReadInt()

		# read number of keys
		numKeys = self.ReadInt()

		for a in range(0, numKeys):
			# read time
			time = self.ReadInt()

			# read keys
			if keyType == 0:
				# read count
				if self.ReadInt() != 4:
					self.ThrowException(
						"Invalid number of arguments for quaternion key in animation")

				time = float(time)
				w = self.ReadFloat()
				x = self.ReadFloat()
				y = self.ReadFloat()
				z = self.ReadFloat()
				key = (time, (w, x, y, z))
				animBone.rotKeys.append(key)

				self.CheckForSemicolon()

			elif keyType == 1 or keyType == 2:
				# read count
				if self.ReadInt() != 3:
					self.ThrowException(
						"Invalid number of arguments for vector key in animation")

				time = float(time)
				value = self.ReadVector3()
				key = (time, value)

				if keyType == 2:
					animBone.posKeys.append(key)
				else:
					animBone.scaleKeys.append(key)

			elif keyType == 3 or keyType == 4:
				# read count
				if self.ReadInt() != 16:
					self.ThrowException(
						"Invalid number of arguments for matrix key in animation")

				# read matrix
				time = float(time)
				a1 = self.ReadFloat()
				b1 = self.ReadFloat()
				c1 = self.ReadFloat()
				d1 = self.ReadFloat()
				a2 = self.ReadFloat()
				b2 = self.ReadFloat()
				c2 = self.ReadFloat()
				d2 = self.ReadFloat()
				a3 = self.ReadFloat()
				b3 = self.ReadFloat()
				c3 = self.ReadFloat()
				d3 = self.ReadFloat()
				a4 = self.ReadFloat()
				b4 = self.ReadFloat()
				c4 = self.ReadFloat()
				d4 = self.ReadFloat()
				animBone.trafoKeys.append(
					(time, (a1, b1, c1, d1, a2, b2, c2, d2, a3, b3, c3, d3, a4, b4, c4, d4)))
				self.CheckForSemicolon()
			else:
				self.ThrowException(
					'Unknown key type %1 in animation.' % keyType)
			self.CheckForSeparator()
		self.CheckForClosingBrace()

	def ParseDataObjectTextureFilename(self) -> bytes:
		self.ReadHeadOfDataObject()
		name = self.GetNextTokenAsString()
		self.CheckForClosingBrace()
		# FIX: some files (e.g. AnimationTest.x) have "" as texture file name
		if not name:
			warn('Unexpected end of file while parsing unknown segment.')
		# some exporters write double backslash paths out. We simply replace them if we find them
		while name.find(b'\\\\') > 0:
			name = name.replace(b'\\\\', b'\\', 1)
		return name

	def ParseUnknownDataObject(self):
		# find opening delimiter
		running = True
		while running:
			t = self.GetNextToken()
			if len(t) == 0:
				self.ThrowException(
					"Unexpected end of file while parsing unknown segment.")

			if t == b"{":
				break

		counter = 1

		# parse until closing delimiter
		while counter > 0:
			t = self.GetNextToken()

			if len(t) == 0:
				self.ThrowException(
					"Unexpected end of file while parsing unknown segment.")

			if t == b"{":
				counter += 1
			elif t == b"}":
				counter -= 1
		return

	def FindNextNoneWhiteSpace(self):
		""" places pointer to next begin of a token, and ignores comments """
		if self.isBinaryFormat:
			return

		running = True
		while running:
			while (self.p < self.end) and (self.buffer[self.p:self.p+1] == b' ' or self.buffer[self.p:self.p+1] == b'\r' or self.buffer[self.p:self.p+1] == b'\n'):
				if self.buffer[self.p:self.p+1] == b'\n':
					self.lineNumber += 1
				self.p += 1
			if self.p >= self.end:
				return
			# check if this is a comment
			if (self.buffer[self.p:self.p+2] == b'//') or self.buffer[self.p:self.p+1] == b'#':
				self.ReadUntilEndOfLine()
				pass
			else:
				break

	def GetNextToken(self) -> bytes:
		""" returns next parseable token. Returns empty string if no token there """
		s = b''

		# process binary-formatted file
		if self.isBinaryFormat:
			# in binary mode it will only return NAME and STRING token
			# and (correctly) skip over other tokens.
			if self.end-self.p < 2:
				return s
			tok = self.ReadBinWord()
			l = 0

			# standalone tokens
			if tok == 1:
				# name token
				if self.end-self.p < 4:
					return s
				l = self.ReadBinDWord()
				bounds = self.end - self.p
				if l < 0:
					return s
				if bounds < l:
					return s
				s = self.buffer[self.p:self.p+l]
				self.p += l
				return s
			elif tok == 2:
				# string token
				if self.end-self.p < 4:
					return s
				l = self.ReadBinDWord()
				if self.end-self.p < l:
					return s
				s = self.buffer[self.p:self.p+l]
				self.p += l+2
				return s
			elif tok == 3:
				# integer token
				self.p += 4
				return b'<integer>'
			elif tok == 5:
				# GUID token
				self.p += 16
				return b'<guid>'
			elif tok == 6:
				if self.end - self.p < 4:
					return s
				l = self.ReadBinDWord()
				self.p += l*4
				return b'<int_list>'
			elif tok == 7:
				if self.end - self.p < 4:
					return s
				l = self.ReadBinDWord()
				self.p += l * self.binaryFloatSize
				return b'<flt_list>'
			elif tok == 0x0a:
				return b'{'
			elif tok == 0x0b:
				return b'}'
			elif tok == 0x0c:
				return b'('
			elif tok == 0x0d:
				return b')'
			elif tok == 0x0e:
				return b'['
			elif tok == 0x0f:
				return b']'
			elif tok == 0x10:
				return b'<'
			elif tok == 0x11:
				return b'>'
			elif tok == 0x12:
				return b"."
			elif tok == 0x13:
				return b","
			elif tok == 0x14:
				return b";"
			elif tok == 0x1f:
				return b"template"
			elif tok == 0x28:
				return b"WORD"
			elif tok == 0x29:
				return b"DWORD"
			elif tok == 0x2a:
				return b"FLOAT"
			elif tok == 0x2b:
				return b"DOUBLE"
			elif tok == 0x2c:
				return b"CHAR"
			elif tok == 0x2d:
				return b"UCHAR"
			elif tok == 0x2e:
				return b"SWORD"
			elif tok == 0x2f:
				return b"SDWORD"
			elif tok == 0x30:
				return b"void"
			elif tok == 0x31:
				return b"string"
			elif tok == 0x32:
				return b"unicode"
			elif tok == 0x33:
				return b"cstring"
			elif tok == 0x34:
				return b"array"

		# process text-formatted file
		else:
			self.FindNextNoneWhiteSpace()
			if self.p >= self.end:
				return s

			while (self.p < self.end) and (not str.isspace(chr(self.buffer[self.p]))):
				# either keep token delimiters when already holding a token, or return if first valid char
				tmp = self.buffer[self.p:self.p+1]
				if tmp == b';' or tmp == b'}' or tmp == b'{' or tmp == b',':
					if not s:
						s += tmp
						self.p += 1
					break  # stop for delimiter
				s += self.buffer[self.p:self.p+1]
				self.p += 1

		return s

	def ReadHeadOfDataObject(self) -> bytes:
		"""reads header of dataobject including the opening brace.
		areturns false if error happened, and writes name of object
		if there is one
		"""
		nameOrBrace = self.GetNextToken()
		if nameOrBrace != b'{':
			if self.GetNextToken() != b'{':
				self.ThrowException("Opening brace expected.")
			return nameOrBrace
		return b''

	def CheckForClosingBrace(self):
		""" checks for closing curly brace, throws exception if not there """
		if self.GetNextToken() != b'}':
			self.ThrowException("Closing brace expected.")

	def CheckForSemicolon(self):
		""" checks for one following semicolon, throws exception if not there """
		if self.isBinaryFormat:
			return
		token = self.GetNextToken()
		if token != b';':
			self.ThrowException("Semicolon expected.")

	def CheckForSeparator(self):
		""" checks for a separator char, either a ',' or a ';' """
		if self.isBinaryFormat:
			return
		token = self.GetNextToken()
		if token != b',' and token != b';':
			self.ThrowException("Separator character (';' or ',') expected.")

	def TestForSeparator(self):
		""" tests and possibly consumes a separator char, but does nothing if there was no separator """
		if self.isBinaryFormat:
			return
		self.FindNextNoneWhiteSpace()
		if self.p >= self.end:
			return
		# test and skip
		# if self.buffer[self.p:self.p+1] == b';' or self.buffer[self.p:self.p+1] == b',':
		if self.buffer[self.p] == 59 or self.buffer[self.p] == 44:
			self.p += 1

	def GetNextTokenAsString(self) -> bytes:
		poString = b''
		""" reads a x file style string """
		if self.isBinaryFormat:
			return self.GetNextToken()

		self.FindNextNoneWhiteSpace()
		if self.p >= self.end:
			self.ThrowException("Unexpected end of file while parsing string")

		if self.buffer[self.p:self.p+1] != b'"':
			self.ThrowException("Expected quotation mark.")
		self.p += 1
		while self.p < self.end and self.buffer[self.p:self.p+1] != b'"':
			poString += self.buffer[self.p:self.p+1]
			self.p += 1

		if self.p >= self.end-1:
			self.ThrowException("Unexpected end of file while parsing string")
		if self.buffer[self.p+1:self.p+2] != b';' or self.buffer[self.p:self.p+1] != b'"':
			self.ThrowException(
				"Expected quotation mark and semicolon at the end of a string.")
		self.p += 2

		return poString

	def ReadUntilEndOfLine(self):
		if self.isBinaryFormat:
			return
		while self.p < self.end:
			tmp = self.buffer[self.p:self.p+1]
			if tmp == b'\n' or tmp == b'\r':
				self.p += 1
				self.lineNumber += 1
				return
			self.p += 1

	def ReadBinWord(self) -> int:
		assert (self.end-self.p >= 2)
		tmp = struct.unpack_from('H', self.buffer, self.p)[0]
		self.p += 2
		return tmp

	def ReadBinDWord(self) -> int:
		assert (self.end-self.p >= 4)
		tmp = struct.unpack_from('I', self.buffer, self.p)[0]
		self.p += 4
		return tmp

	def ReadInt(self) -> int:
		if self.isBinaryFormat:
			if self.binaryNumCount == 0 and (self.end-self.p >= 2):
				tmp = self.ReadBinWord()
				if tmp == 0x06 and (self.end-self.p >= 4):
					self.binaryNumCount = self.ReadBinDWord()
				else:
					self.binaryNumCount = 1

			self.binaryNumCount -= 1
			if self.end-self.p >= 4:
				return self.ReadBinDWord()
			else:
				self.p = self.end
				return 0
		else:
			self.FindNextNoneWhiteSpace()

			# check preceeding minus sign
			isNegative = False
			if self.buffer[self.p:self.p+1] == b'-':
				isNegative = False
				self.p += 1
			# at least one digit expected
			if not self.buffer[self.p:self.p+1].isdigit():
				self.ThrowException('Number expected.')

			# read digits
			number = 0
			while self.p < self.end:
				if not self.buffer[self.p:self.p+1].isdigit():
					break
				number = number * 10 + int(self.buffer[self.p:self.p+1])
				self.p += 1

			self.CheckForSeparator()
			if isNegative:
				return -number
			else:
				return number

	def ReadFloat(self) -> float:
		if self.isBinaryFormat:
			if (self.binaryNumCount == 0) and (self.end - self.p >= 2):
				tmp = self.ReadBinWord()
				if(tmp == 0x07) and (self.end - self.p >= 4):
					self.binaryNumCount = self.ReadBinDWord()
				else:
					self.binaryNumCount = 1
			self.binaryNumCount -= 1
			if self.binaryFloatSize == 8:
				if self.end-self.p >= 8:
					result = struct.unpack_from('d', self.buffer, self.p)[0]
					self.p += 8
					return result
				else:
					self.p = self.end
					return 0
			else:
				if self.end - self.p >= 4:
					result = struct.unpack_from('f', self.buffer, self.p)[0]
					self.p += 4
					return result
				else:
					self.p = self.end
					return 0

		# text version
		self.FindNextNoneWhiteSpace()
		# check for various special strings to allow reading files from faulty exporters
		# I mean you, Blender!
		# Reading is safe because of the terminating zero

		if self.buffer[self.p:self.p+9] == b'-1.#IND00' or self.buffer[self.p:self.p+8] == b'1.#IND00':
			self.p += 9
			self.CheckForSeparator()
			return 0.0
		elif self.buffer[self.p:self.p+8] == b'1.#QNAN0':
			self.p += 8
			self.CheckForSeparator()
			return 0.0
		result_ = 0.0
		#tmp_ = ''
		digitStart = self.p
		digitEnd = self.p
		notSplitChar = [b'0', b'1', b'2', b'3', b'4', b'5',
						b'6', b'7', b'8', b'9', b'+', b'.', b'-', b'e', b'E']
		while self.p < self.end:
			c = self.buffer[self.p:self.p+1]
			# if c.isdigit() or c=='+' or c=='.' or c=='-' or c=='e' or c=='E':
			if c in notSplitChar:
				#tmp_ += c
				digitEnd = self.p
				self.p += 1
			else:
				break
		tmp = self.buffer[digitStart:digitEnd]
		result_ = float(tmp)
		self.CheckForSeparator()
		return result_

	def ReadVector2(self) -> tuple[float, float]:
		x = self.ReadFloat()
		y = self.ReadFloat()
		self.TestForSeparator()
		return (x, y)

	def ReadVector3(self) -> tuple[float, float, float]:
		x = self.ReadFloat()
		y = self.ReadFloat()
		z = self.ReadFloat()
		self.TestForSeparator()
		return (x, y, z)

	def ReadRGB(self) -> tuple[float, float, float]:
		r = self.ReadFloat()
		g = self.ReadFloat()
		b = self.ReadFloat()
		self.TestForSeparator()
		return (r, g, b)

	def ReadRGBA(self) -> tuple[float, float, float, float]:
		r = self.ReadFloat()
		g = self.ReadFloat()
		b = self.ReadFloat()
		a = self.ReadFloat()
		self.TestForSeparator()
		return (r, g, b, a)

	def ThrowException(self, text: str):
		"""Throws an exception with a line number and the given text."""
		if(self.isBinaryFormat):
			raise ImportError(text)
		else:
			raise ImportError('Line %d: %s' % (self.lineNumber, text))

	def FilterHierarchy(self, node: Node):
		"""Filters the imported hierarchy for some degenerated cases that some
		exporters produce."""

		# if the node has just a single unnamed child containing a mesh, remove
		# the anonymous node inbetween. The 3DSMax kwXport plugin seems to produce this
		# mess in some cases
		if(len(node.children) == 1 and not node):
			child = node.children[0]
			if (not child.name and child.meshes.cout > 0):
				# transfer its meshes to us
				for a in range(0, child.meshes.cout):
					node.meshes.append(child.meshes[a])
				child.meshes = []

				# transfer the transform as well
				node.trafoMatrix = node.trafoMatrix * child.trafoMatrix

				# then kill it
				del(child)
				node.children = []

		# recurse
		for a in range(0, len(node.children)):
			self.FilterHierarchy(node.children[a])

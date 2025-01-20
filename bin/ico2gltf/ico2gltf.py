#! /bin/env python3

import struct
import unicodedata
from io import BytesIO
from pathlib import PurePath
from ps2ico import Ps2ico
from ps2sys import Ps2sys
from argparse import ArgumentParser
from PIL import Image as PILImage
from gltflib import (
    GLTF, GLTFModel, Asset, Scene, Node, Mesh, Primitive, Attributes, Buffer, BufferView, Accessor, AccessorType, Image, Target,
	Animation, AnimationSampler, AnimationTargetPath, BufferTarget, ComponentType, GLBResource, FileResource, Texture, Sampler,
	Interpolation, Material, PBRMetallicRoughness, TextureInfo, Channel
)

VERSION = "0.2"

def convert_color(color):
	return ((8 * (color >> 10)) & 0xFF, (8 * ((color >> 5) & 0x1F)) & 0xFF, (8 * (color & 0x1F)) & 0xFF)

def convert_uncompressed_texture_data(data):
	result = bytearray()

	for i in range(128 * 128):
		result.extend(convert_color(data[i]))

	return bytes(reversed(result))

def convert_compressed_texture_data(size, data):
	offset = 0
	result = bytearray()

	while offset < size / 2:
		code = data[offset]
		offset += 1

		if code == 0:
			continue

		if code < 0xFF00:
			color = convert_color(data[offset])
			offset += 1
			result.extend(color * code)
		else:
			for _ in range(0xFFFF - code + 1):
				color = convert_color(data[offset])
				offset += 1
				result.extend(color)

	return bytes(reversed(result))

def export_gltf(icon, filename, metadata=None):
	basename = PurePath(filename).stem

	vertex_info_format = ("3f" * icon.animation_shapes) + "3f 2f 3f"
	float_size = struct.calcsize("f")
	animation_speed = 0.1

	animation_present = icon.animation_shapes > 1

	model_data = bytearray()

	mins = {}
	maxs = {}
		
	for i, vertex in enumerate(icon.vertices):
		for j, position in enumerate(vertex.positions):
			if j == 0:
				values_basis = [position.x / 4096, -position.y / 4096, -position.z / 4096]
				values = values_basis
			else:
				# Subtract basis position to compensate for shape keys being relative to basis
				values = [position.x / 4096 - values_basis[0], -position.y / 4096 - values_basis[1], -position.z / 4096 - values_basis[2]]

			if j not in mins:
				mins[j] = values.copy()
			else:
				if values[0] < mins[j][0]: mins[j][0] = values[0]
				if values[1] < mins[j][1]: mins[j][1] = values[1]
				if values[2] < mins[j][2]: mins[j][2] = values[2]
			
			if j not in maxs:
				maxs[j] = values.copy()
			else:
				if values[0] > maxs[j][0]: maxs[j][0] = values[0]
				if values[1] > maxs[j][1]: maxs[j][1] = values[1]
				if values[2] > maxs[j][2]: maxs[j][2] = values[2]

			model_data.extend(struct.pack("3f", *values))

		model_data.extend(struct.pack("3f 2f 3f", 
			vertex.normal.x / 4096, -vertex.normal.y / 4096, -vertex.normal.z / 4096,
			1.0 - (vertex.tex_coord.u / 4096), 1.0 - (vertex.tex_coord.v / 4096),
			vertex.color.r / 255, vertex.color.g / 255, vertex.color.b / 255)
		)

	# Generate animation data if multiple animation shapes are present

	if animation_present:
		animation_offset = len(model_data)

		for i in range(icon.frame_count + 1):
			model_data.extend(struct.pack("f", i * animation_speed))

		for i, frame in enumerate(icon.frames + [icon.frames[0]]):
			segment = [struct.pack("f", 0.0)] * (icon.animation_shapes - 1)
			
			if frame.shape_id != 0:
				segment[frame.shape_id - 1] = struct.pack("f", 1.0)

			for item in segment:
				model_data.extend(item)

		animation_length = len(model_data) - animation_offset

	# Generate texture

	if isinstance(icon.texture, Ps2ico.CompressedTexture):
		image_data = convert_compressed_texture_data(icon.texture.size, icon.texture.data)
	elif isinstance(icon.texture, Ps2ico.UncompressedTexture):
		image_data = convert_uncompressed_texture_data(icon.texture.data)

	with BytesIO() as png:
		PILImage.frombytes("RGB", (128, 128), image_data).save(png, "png")
		texture_data = png.getvalue()

	# Basic glTF info

	model = GLTFModel()
	
	model.asset = Asset(
		version="2.0",
		generator=f"ico2gltf v{VERSION}"
	)

	model.scenes = [
		Scene(nodes=[0])
	]

	model.scene = 0

	model.nodes = [
		Node(mesh=0)
	]

	# If present, embed metadata

	if metadata:
		# Normalize title: turn japanese full-width characters into normal ones and insert the line break
		title = unicodedata.normalize("NFKC", metadata.title).rstrip("\x00")
		title = title[:metadata.offset_2nd_line // 2] + "\n" + title[metadata.offset_2nd_line // 2:]

		model.extras = {
			"title": title,
			"background_opacity": metadata.bg_opacity / 0x80,
			"background_bottom_left_color": [
				metadata.bg_color_lowerleft.r / 0x80, 
				metadata.bg_color_lowerleft.g / 0x80, 
				metadata.bg_color_lowerleft.b / 0x80,
				metadata.bg_color_lowerleft.a / 0x80
			],
			"background_bottom_right_color": [
				metadata.bg_color_lowerright.r / 0x80, 
				metadata.bg_color_lowerright.g / 0x80, 
				metadata.bg_color_lowerright.b / 0x80,
				metadata.bg_color_lowerright.a / 0x80
			],
			"background_top_left_color": [
				metadata.bg_color_upperleft.r / 0x80, 
				metadata.bg_color_upperleft.g / 0x80, 
				metadata.bg_color_upperleft.b / 0x80, 
				metadata.bg_color_upperleft.a / 0x80
			],
			"background_top_right_color": [
				metadata.bg_color_upperright.r / 0x80, 
				metadata.bg_color_upperright.g / 0x80, 
				metadata.bg_color_upperright.b / 0x80, 
				metadata.bg_color_lowerright.a / 0x80
			],
			"ambient_color": [metadata.light_ambient_color.r, metadata.light_ambient_color.g, metadata.light_ambient_color.b],
			"light1_direction": [metadata.light1_direction.x, metadata.light1_direction.y, metadata.light1_direction.z],
			"light1_color": [metadata.light1_color.r, metadata.light1_color.g, metadata.light1_color.b, metadata.light1_color.a],
			"light2_direction": [metadata.light2_direction.x, metadata.light2_direction.y, metadata.light2_direction.z],
			"light2_color": [metadata.light2_color.r, metadata.light2_color.g, metadata.light2_color.b, metadata.light2_color.a],
			"light3_direction": [metadata.light3_direction.x, metadata.light3_direction.y, metadata.light3_direction.z],
			"light3_color": [metadata.light3_color.r, metadata.light3_color.g, metadata.light3_color.b, metadata.light3_color.a],
		}

	# Meshes

	primitive = Primitive(
		attributes=Attributes(
			POSITION=0, 
			NORMAL=icon.animation_shapes, 
			TEXCOORD_0=icon.animation_shapes + 1,
			COLOR_0=icon.animation_shapes + 2
		),
		material=0
	)

	if animation_present:
		primitive.targets = [{"POSITION": i + 1} for i in range(icon.animation_shapes - 1)]

	model.meshes = [
		Mesh(name="Icon", primitives=[primitive])
	]

	# Buffers

	model.buffers = [
		Buffer(uri=f"{basename}.bin", byteLength=len(model_data)),
		Buffer(uri=f"{basename}.png", byteLength=len(texture_data))
	]

	# Materials

	model.images = [
		Image(bufferView=1, mimeType="image/png")
	]

	model.textures = [
		Texture(source=0)
	]

	model.materials=[
		Material(name="Material", pbrMetallicRoughness=PBRMetallicRoughness(
			baseColorTexture=TextureInfo(index=0),
			roughnessFactor=1,
			metallicFactor=0
		))
	]

	# Animations

	if animation_present:
		model.animations = [
			Animation(name="Default",
				samplers=[
					AnimationSampler(
						input=icon.animation_shapes + 3,
						output=icon.animation_shapes + 4,
						interpolation=Interpolation.LINEAR.value
					)
				],
				channels=[Channel(sampler=0, target=Target(node=0, path="weights"))]
			),
		]

	# Buffer Views

	model.bufferViews=[
		BufferView(name="Data", buffer=0, byteStride=struct.calcsize(vertex_info_format), byteLength=len(model_data)),
		BufferView(name="Texture", buffer=1, byteLength=len(texture_data)),
	]

	if animation_present:
		model.bufferViews.append(
			BufferView(name="Animation", buffer=0, byteOffset=animation_offset, byteLength=animation_length),
		)

	# Accessors

	model.accessors=[
		Accessor(name=f"Position {i}", bufferView=0, byteOffset=i * 3 * float_size, min=mins[i], max=maxs[i], 
			count=len(icon.vertices), componentType=ComponentType.FLOAT.value, type=AccessorType.VEC3.value) for i in range(icon.animation_shapes)
	]
	
	model.accessors.extend([	
		Accessor(name="Normal", bufferView=0, byteOffset=((icon.animation_shapes - 1) * 3 * float_size) + 3 * float_size, 
			count=len(icon.vertices), componentType=ComponentType.FLOAT.value, type=AccessorType.VEC3.value),
		Accessor(name="UV", bufferView=0, byteOffset=((icon.animation_shapes - 1) * 3 * float_size) + 6 * float_size, 
			count=len(icon.vertices), componentType=ComponentType.FLOAT.value, type=AccessorType.VEC2.value),
		Accessor(name="Color", bufferView=0, byteOffset=((icon.animation_shapes - 1) * 3 * float_size) + 8 * float_size, 
			count=len(icon.vertices), componentType=ComponentType.FLOAT.value, type=AccessorType.VEC3.value),
	])

	if animation_present:
		model.accessors.extend([
			Accessor(name="Animation Time", bufferView=2, byteOffset=0, min=[0.0], max=[(icon.frame_count) * animation_speed],
				count=(icon.frame_count + 1), componentType=ComponentType.FLOAT.value, type=AccessorType.SCALAR.value),
			Accessor(name="Animation Data", bufferView=2, byteOffset=(icon.frame_count + 1) * float_size, min=[0.0], max=[1.0],
				count=(icon.frame_count + 1) * (icon.animation_shapes - 1), componentType=ComponentType.FLOAT.value, type=AccessorType.SCALAR.value)
		])

	resources = [
		FileResource(f"{basename}.bin", data=model_data),
		FileResource(f"{basename}.png", data=texture_data)
	]

	gltf = GLTF(model=model, resources=resources)
	gltf.export(filename)

def main():
	parser = ArgumentParser(
		description="Convert PS2 save icons to glTF.",
	)

	parser.add_argument("input", type=str,
		help="Input file (.ico)."
	)

	parser.add_argument("-o", "--output", type=str,
		help="Output file (.glb or .gltf). If not specified create a .glb file next to input file with the same file name."
	)

	parser.add_argument("-m", "--metadata", type=str, default=None,
		help="Path to an icon.sys file with extra information to be embedded as an \"extras\" field."
	)

	parser.add_argument("-q", "--quiet", default=False, action="store_const", const=True,
		help="Do not print any icon info."
	)

	parser.add_argument("-v", "--version", action="version", version=f"{VERSION}")

	args = parser.parse_args()

	if args.output is None:
		args.output = PurePath(args.input).with_suffix(".glb").as_posix()
	
	metadata = None

	if args.metadata:
		metadata = Ps2sys.from_file(args.metadata)

	icon = Ps2ico.from_file(args.input)
	export_gltf(icon, args.output, metadata)

	if not args.quiet:
		print(f"ico2gltf v{VERSION}")
		print(f"Converted {PurePath(args.input).name} to {PurePath(args.output).name}")
		print("---------------------------------------------------")
		print(f"Animation shapes:\t{icon.animation_shapes}")
		print(f"Frame count:\t\t{icon.frame_count}")
		print(f"Texture type:\t\t0x{icon.texture_type:02X}")

if __name__ == "__main__":
	main()

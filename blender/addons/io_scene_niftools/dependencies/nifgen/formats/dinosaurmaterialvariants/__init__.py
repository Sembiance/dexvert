from nifgen.formats.dinosaurmaterialvariants.imports import name_type_map
# an experiment
import logging
import os

from nifgen.formats.dinosaurmaterialvariants.compounds.DinoLayersHeader import DinoLayersHeader
from nifgen.formats.fgm.compounds.FgmHeader import FgmHeader
from nifgen.formats.ovl_base import OvlContext


channels = ("R", "G", "B", "A")


class LayeredMaterial:

	def __init__(self):
		self.context = OvlContext()
		self.slots = []

	def create_node(self):
		pass

	def load_mat_layers(self, layers_path):
		base_dir, layers_name = os.path.split(layers_path)
		basename, ext = os.path.splitext(layers_name)
		matname = basename.split("_layers")[0]
		logging.info(f"Material: {matname}")
		layers_root = DinoLayersHeader.from_xml_file(layers_path, self.context)
		tile_i = 0
		ch_i = 0
		for mask_i, layer in enumerate(layers_root.layers.data):
			mask_png_path = os.path.join(base_dir, f"{matname}.playered_blendweights_[{tile_i:02}]_{channels[ch_i]}.png")
			# increment channel
			if layer.has_ptr:
				ch_i += 1
			# move to the next tile for the next loop
			if ch_i == 4:
				ch_i = 0
				tile_i += 1
			tex_fgm_path = get_fgm_path(base_dir, layer.texture_fgm_name)
			trans_fgm_path = get_fgm_path(base_dir, layer.transform_fgm_name)
			if not os.path.isfile(mask_png_path):
				logging.info(f"Found no mask texture for layer {mask_i}")
			elif not tex_fgm_path:
				logging.info(f"No texture fgm for layer {mask_i}")
			elif not trans_fgm_path:
				logging.info(f"No transform fgm for layer {mask_i}")
			else:
				logging.info(f"Layer {mask_i} is tiled")
				if os.path.isfile(tex_fgm_path) and os.path.isfile(trans_fgm_path):
					logging.info(f"Found .fgm files for layer")
					tex_fgm = FgmHeader.from_xml_file(tex_fgm_path, self.context)
					trans_fgm = FgmHeader.from_xml_file(trans_fgm_path, self.context)
					height_tex = tex_fgm.textures.data[1]
					height_dep = tex_fgm.name_foreach_textures.data[1]
					height_file_name = height_dep.dependency_name.data
					height_file_basename = os.path.splitext(height_file_name)[0]
					# todo codegen - why is array_index str, not int?
					array_index = int(height_tex.value[0].array_index)
					height_tile_png_path = os.path.join(base_dir, f"{height_file_basename}_[{array_index:02}].png")
					if not os.path.isfile(height_tile_png_path):
						logging.error(f"Found no tile texture for layer {mask_i} {height_tile_png_path}")
					self.slots.append(Layer(mask_png_path, height_tile_png_path, trans_fgm))
				else:
					logging.error(f"Fgm files for layer {mask_i} are missing")


class Layer:

	def __init__(self, mask_png_path, height_tile_png_path, trans_fgm):
		self.mask_png_path = mask_png_path
		self.height_tile_png_path = height_tile_png_path
		self.trans_fgm = trans_fgm
		self.lut = {}
		for attrib, attrib_data in zip(self.trans_fgm.attributes.data, self.trans_fgm.value_foreach_attributes.data):
			# skip first letter p
			self.lut[attrib.name.lower()[1:]] = attrib_data.value
		# print(self.trans_fgm)
		# print(self.lut)


def get_fgm_path(base_dir, fgm_name_ptr):
	fgm_basename = fgm_name_ptr.data
	if fgm_basename:
		fgm_path = os.path.join(base_dir, f"{fgm_basename}.fgm")
		return fgm_path


if __name__ == "__main__":
	# load_mat_layers("C:/Users/arnfi/Desktop/anim/tylosaurus_layers.dinosaurmateriallayers")
	layers = LayeredMaterial()
	layers.load_mat_layers("C:/Users/arnfi/Desktop/ichthyo/ichthyosaurus_layers.dinosaurmateriallayers")

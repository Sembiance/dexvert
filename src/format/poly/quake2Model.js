import {Format} from "../../Format.js";

export class quake2Model extends Format
{
	name       = "Quake 2 Model";
	website    = "http://fileformats.archiveteam.org/wiki/MD2";
	ext        = [".md2"];
	magic      = ["Quake 2 model", "Quake II 3D Model file"];
	converters = ["assimp", "blender[format:md2]", "milkShape3D[format:quake2Model]", "threeDObjectConverter"];
}

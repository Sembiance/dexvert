import {Format} from "../../Format.js";

export class quake2Model extends Format
{
	name       = "Quake 2 Model";
	website    = "http://fileformats.archiveteam.org/wiki/MD2";
	ext        = [".md2"];
	magic      = ["Quake 2 model"];
	converters = ["assimp", "blender[format:md2]"];
}

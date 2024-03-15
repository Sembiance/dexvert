import {Format} from "../../Format.js";

export class ac3d extends Format
{
	name       = "AC3D Model";
	website    = "http://fileformats.archiveteam.org/wiki/AC3D_Model";
	ext        = [".ac", ".ac3d"];
	magic      = ["AC3D geometry/model"];
	converters = ["blender[format:ac3d]", "assimp", "threeDObjectConverter"];
}

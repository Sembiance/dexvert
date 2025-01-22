import {Format} from "../../Format.js";

export class quake3Model extends Format
{
	name       = "Quake 3 Model";
	website    = "http://fileformats.archiveteam.org/wiki/MD3";
	ext        = [".md3"];
	magic      = ["Quake III Arena model"];
	converters = ["assimp", "noesis[type:poly]", "milkShape3D[format:quake3Model][matchType:magic]", "threeDObjectConverter[matchType:magic]"];
}

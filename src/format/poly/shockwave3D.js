import {Format} from "../../Format.js";

export class shockwave3D extends Format
{
	name       = "Shockwave 3D Scene";
	website    = "http://fileformats.archiveteam.org/wiki/Wavefront_OBJ";
	ext        = [".w3d"];
	magic      = ["Shockwave 3D Scene Export", "Format: Shockwave 3D"];
	converters = ["shockwave3DWorldConverter"];
}

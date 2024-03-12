import {Format} from "../../Format.js";

export class lightWave extends Format
{
	name       = "LightWave 3D Object";
	website    = "http://fileformats.archiveteam.org/wiki/LightWave_Object";
	ext        = [".lwo", ".lwob", ".lw", ".lightwave"];
	magic      = ["IFF data, LWOB 3-D object", "LightWave 3D Object", "IFF data, LWLO 3-D layered object", /^fmt\/1205( |$)/];
	converters = ["blender[format:lwo]", "AccuTrans3D", "assimp", "cinema4D427", "milkShape3D[format:lightWave]"];
	// Lightwave 3D 7.0 from Twilight DVD #64 running under WinXP can also open these but it chokes on very big files and doesn't seem to do any better than blender
}

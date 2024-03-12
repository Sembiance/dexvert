import {Format} from "../../Format.js";

export class luxology3DScene extends Format
{
	name       = "Luxology 3D Scene";
	website    = "http://fileformats.archiveteam.org/wiki/LXO";
	ext        = [".lxo"];
	magic      = ["Luxology 3D scene"];
	converters = ["assimp", "blender[format:lxo]", "AccuTrans3D"];
}

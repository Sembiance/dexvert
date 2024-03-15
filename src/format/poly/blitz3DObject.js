import {Format} from "../../Format.js";

export class blitz3DObject extends Format
{
	name       = "Blitz3D Object";
	website    = "http://fileformats.archiveteam.org/wiki/Blitz3D_Model";
	ext        = [".b3d"];
	magic      = ["Blitz3d object", "Blitz3D Model", /^fmt\/1182( |$)/];
	converters = ["blender[format:b3d]", "assimp", "threeDObjectConverter"];
}

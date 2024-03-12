import {Format} from "../../Format.js";

export class kaydaraFilmboxModel extends Format
{
	name        = "Kaydara Filmbox Model";
	website     = "http://fileformats.archiveteam.org/wiki/FBX";
	ext         = [".fbx"];
	magic       = ["Kaydara FBX model", "Autodesk - Kaydara FBX 3D format", /^fmt\/1009( |$)/];
	converters  = ["milkShape3D[format:fbx]", "blender[format:fbx]", "assimp"];
	notes       = "Both assimp and blender only support much more modern versions of this format";
}

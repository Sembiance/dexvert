import {Format} from "../../Format.js";

export class doom3Mesh extends Format
{
	name       = "Doom 3 Mesh";
	website    = "https://modwiki.dhewm3.org/MD5MESH_(file_format)";
	ext        = [".md5mesh"];
	magic      = ["Doom 3 MD5 Mesh"];
	converters = ["blender[format:md5mesh]", "assimp", "milkShape3D[format:doom3Mesh]", "threeDObjectConverter"];
}

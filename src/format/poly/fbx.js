import {Format} from "../../Format.js";

export class fbx extends Format
{
	name       = "Kaydara Filmbox Model";
	website    = "http://fileformats.archiveteam.org/wiki/FBX";
	ext        = [".fbx", ".fbx4"];
	magic      = ["Kaydara FBX model", "Autodesk - Kaydara FBX 3D format", "Format: Kaydara FBX Binary", /^fmt\/(1009|1010)( |$)/];
	converters = ["polyTrans64[format:fbx6]", "polyTrans64[format:fbx5]", "polyTrans64[format:fbx7]", "milkShape3D[format:fbx]", "blender[format:fbx]", "assimp", "threeDObjectConverter", "noesis[type:poly]"];
}

import {Format} from "../../Format.js";

export class collada extends Format
{
	name           = "MilkShape 3D Model";
	website        = "http://fileformats.archiveteam.org/wiki/COLLADA";
	ext            = [".dae", ".zae", ".xml"];
	forbidExtMatch = [".xml"];
	magic          = ["COLLADA model, XML document", "COLLADA Digital Asset Document", /^fmt\/1209( |$)/];
	converters     = ["blender[format:collada]", "assimp"];
}

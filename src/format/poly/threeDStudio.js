import {Format} from "../../Format.js";

export class threeDStudio extends Format
{
	name           = "3D Studio";
	website        = "http://fileformats.archiveteam.org/wiki/3DS";
	ext            = [".3ds", ".max", ".asc"];
	forbidExtMatch = [".asc"];
	magic          = ["3D Studio model", "3D Studio mesh", "3D Studio Max Scene", "3D Studio ASCII format", /^fmt\/978( |$)/, /^x-fmt\/19( |$)/];
	converters     = ["blender[format:3ds]", "polyTrans64[format:threeDStudio]", "assimp"];
}

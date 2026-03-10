import {Format} from "../../Format.js";

export class threeMF extends Format
{
	name           = "3D Manufacturing Format";
	website        = "http://fileformats.archiveteam.org/wiki/3MF";
	ext            = [".3mf"];
	forbidExtMatch = true;	// too modern, unlikely to match
	magic          = ["3D Manufacturing Format model", /^fmt\/829( |$)/];
	converters     = ["blender[format:3mf]", "assimp"];
}

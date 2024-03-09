import {Format} from "../../Format.js";

export class wavefrontOBJ extends Format
{
	name           = "Wavefront OBJ";
	website        = "http://fileformats.archiveteam.org/wiki/Wavefront_OBJ";
	ext            = [".obj"];
	forbidExtMatch = true;
	magic          = ["Wavefront Object", /^fmt\/1210( |$)/];
	converters     = ["blender[format:obj]", "assimp"];
}

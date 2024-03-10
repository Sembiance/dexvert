import {Format} from "../../Format.js";

export class wavefrontOBJ extends Format
{
	name           = "Wavefront OBJ";
	website        = "http://fileformats.archiveteam.org/wiki/Wavefront_OBJ";
	ext            = [".obj"];
	forbidExtMatch = true;
	magic          = ["Wavefront Object", /^fmt\/1210( |$)/];
	auxFiles       = (input, otherFiles) => (otherFiles.some(o => o.ext.toLowerCase()===".mtl") ? otherFiles.filter(o => o.ext.toLowerCase()===".mtl") : []);
	converters     = ["blender[format:obj]", "assimp"];
}

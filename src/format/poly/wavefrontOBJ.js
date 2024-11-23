import {Format} from "../../Format.js";

export class wavefrontOBJ extends Format
{
	name       = "Wavefront OBJ";
	website    = "http://fileformats.archiveteam.org/wiki/Wavefront_OBJ";
	ext        = [".obj"];
	magic      = [
		// generic
		"Wavefront Object", "UVMapper object", "model/obj", /^fmt\/(1|1210)( |$)/,

		// specific
		"CADRazor 3d model"
	];
	idMeta   = ({macFileType, macFileCreator}) => macFileType==="PCFL" && macFileCreator==="SWIN";
	auxFiles = (input, otherFiles) =>
	{
		const supportFiles = otherFiles.filter(o => [".mtl", ".tiff", ".tif"].includes(o.ext.toLowerCase()));
		return supportFiles.length===0 ? false : supportFiles;
	};
	keepFilename = true;
	converters   = ["blender[format:obj]", "assimp", "milkShape3D[matchType:magic][format:wavefront]"];
}

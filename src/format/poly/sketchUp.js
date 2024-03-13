import {Format} from "../../Format.js";

export class sketchUp extends Format
{
	name           = "SketchUp Model";
	website        = "http://fileformats.archiveteam.org/wiki/SKP";
	ext            = [".skp"];
	forbidExtMatch = true;	// Maybe remove this once I convert this format as an actual 3D model
	magic          = ["SketchUp Model", "SketchUp model", "Google SketchUp Model", /^fmt\/(1265|1266)( |$)/];
	unsupported    = true;
	notes          = "Couldn't find a working converter. This one for Blender failed in Blender 4 on Linux: https://github.com/RedHaloStudio/Sketchup_Importer/releases/tag/0.23.2";
}

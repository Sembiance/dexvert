import {Format} from "../../Format.js";

export class valveSMD extends Format
{
	name           = "Valve Studiomdl Data";
	website        = "http://fileformats.archiveteam.org/wiki/Studiomdl_Data";
	ext            = [".smd"];
	forbidExtMatch = true;
	magic          = ["Valve Studiomdl Data"];
	converters     = ["blender[format:smd]", "assimp"];
}

import {Format} from "../../Format.js";

export class valveSMD extends Format
{
	name           = "Valve Studiomdl Data";
	ext            = [".smd"];
	forbidExtMatch = true;
	magic          = ["Valve Studiomdl Data"];
	converters     = ["blender[format:smd]", "assimp"];
}

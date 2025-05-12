import {Format} from "../../Format.js";

export class gfaRaytraceBitmap extends Format
{
	name           = "GFA Raytrace bitmap";
	website        = "https://www.atari-wiki.com/index.php?title=GFA_Raytrace_file_format";
	ext            = [".sul", ".scl", ".suh", ".sch"];
	forbidExtMatch = true;
	magic          = [/^GFA Raytrace .*image .*bitmap$/];
	converters     = ["nconvertWine"];
}

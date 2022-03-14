import {Format} from "../../Format.js";

export class visio extends Format
{
	name           = "Microsoft Visio";
	website        = "http://fileformats.archiveteam.org/wiki/Visio";
	ext            = [".vsd", ".vss", ".vst", ".vdx", ".vsx", ".vtx"];
	forbidExtMatch = true;
	magic          = ["Visio Drawing", "Microsoft Visio Drawing"];
	converters     = ["soffice"];
}

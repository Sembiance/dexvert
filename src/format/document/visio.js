import {Format} from "../../Format.js";

export class visio extends Format
{
	name           = "Microsoft Visio";
	website        = "http://fileformats.archiveteam.org/wiki/Visio";
	ext            = [".vsd", ".vss", ".vst", ".vdx", ".vsx", ".vtx"];
	forbidExtMatch = true;
	magic          = ["Visio Drawing", "Microsoft Visio Drawing", "Microsoft Visio Stencil", /^fmt\/(216|443|1508|1509|1510)( |$)/, /^x-fmt\/(113|258)( |$)/];
	converters     = ["soffice[format:VisioDocument]"];
}

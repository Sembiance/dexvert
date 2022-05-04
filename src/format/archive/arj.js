import {Format} from "../../Format.js";

export class arj extends Format
{
	name           = "ARJ Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ARJ";
	ext            = [".arj", ".exe"];
	forbidExtMatch = [".exe"];
	magic          = ["ARJ compressed archive", "ARJ File Format", "ARJ archive data", "ARJ self-extracting archive", /^fmt\/610( |$)/];
	converters     = ["unar", "UniExtract"];
}

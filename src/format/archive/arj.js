import {Format} from "../../Format.js";

export class arj extends Format
{
	name           = "ARJ Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ARJ";
	ext            = [".arj", ".exe"];
	forbidExtMatch = [".exe"];
	magic          = ["ARJ compressed archive", "ARJ File Format", "ARJ archive data", "ARJ self-extracting archive", "ARJ Archiv gefunden", /^ARJ$/, /^fmt\/610( |$)/];
	converters     = ["unar", "arj", "sqc", "izArc", "UniExtract", "deark[module:arj]"];	// deark is last because it doesn't create output directories so with BILLY.ARJ LIST/BILLY.DOC is extracted as LIST_BILLY.DOC
}

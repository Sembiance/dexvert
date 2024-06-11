import {Format} from "../../Format.js";
import {_MS_WORKS_DB_MAGIC} from "./microsoftWorksDatabase.js";

export class microsoftWorks extends Format
{
	name           = "Microsoft Works Document";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Works";
	ext            = [".wps", ".wp", ".doc"];
	forbidExtMatch = true;
	magic          = ["Microsoft Works", "Composite Document File", /^OLE 2 Compound Document.* Microsoft Works.* document/, "Microsoft Works Spreadsheet", /^fmt\/(163|166|233|258)( |$)/];
	forbiddenMagic = _MS_WORKS_DB_MAGIC;
	weakMagic      = ["Microsoft Works", "Composite Document File", /^OLE 2 Compound Document.* Microsoft Works.* document/];
	converters     = ["keyViewPro[outType:pdf]", "fileMerlin[type:MSWKW*]", "soffice[format:MS Works]", "soffice[format:MS Works Calc]", "wordForWord"];
}

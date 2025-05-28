import {Format} from "../../Format.js";
import {_MS_WORKS_DB_MAGIC} from "./microsoftWorksDatabase.js";

export class microsoftWorks extends Format
{
	name           = "Microsoft Works Document/Spreadsheet";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Works";
	ext            = [".wps", ".wp", ".doc", ".xlr"];
	forbidExtMatch = true;
	magic          = ["Microsoft Works", "Composite Document File", "Works 4.0 for Macintosh", /^OLE 2 Compound Document.* Microsoft Works.* document/, "Microsoft Works Spreadsheet", /^fmt\/(163|166|233|258|901)( |$)/];
	forbiddenMagic = _MS_WORKS_DB_MAGIC;
	converters     = ["keyViewPro[outType:pdf]", "fileMerlin[type:MSWKW*]", "soffice[format:MS Works]", "soffice[format:MS Works Calc]", "wordForWord"];
}

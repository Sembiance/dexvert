import {Format} from "../../Format.js";

export class openDocument extends Format
{
	name           = "Open Document Format for Office Applications";
	website        = "http://fileformats.archiveteam.org/wiki/OpenDocument";
	ext            = [".odm", ".odt", ".fodt", ".ott", ".odp", ".ods", ".otp"];
	forbidExtMatch = true;
	magic          = [
		// general
		"OpenDocument Text", "OpenDocument Master Text document", "OpenDocument Master Document", "OpenDocument Presentation", "OpenDocument Spreadsheet document", "OpenDocument Spreadsheet",  /^fmt\/(138|291|293|295|1754|1755|1756)( |$)/,
	
		// specific
		"XMind Workbook"
	];
	converters     = ["soffice[matchType:magic]"];
}

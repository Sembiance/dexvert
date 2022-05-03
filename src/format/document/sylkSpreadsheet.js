import {Format} from "../../Format.js";

export class sylkSpreadsheet extends Format
{
	name           = "SYmbolic LinK Spreadsheet";
	website        = "http://fileformats.archiveteam.org/wiki/SYLK";
	ext            = [".slk", ".sylk"];
	forbidExtMatch = true;
	magic          = ["spreadsheet interchange document"];
	converters     = ["soffice"];
}

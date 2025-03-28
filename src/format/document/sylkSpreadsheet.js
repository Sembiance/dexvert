import {Format} from "../../Format.js";

export class sylkSpreadsheet extends Format
{
	name           = "SYmbolic LinK Spreadsheet";
	website        = "http://fileformats.archiveteam.org/wiki/SYLK";
	ext            = [".slk", ".sylk"];
	forbidExtMatch = true;
	magic          = [
		// generic
		"spreadsheet interchange document", "SYLK - SYmbolic LinK data", "Microsoft SYLK", "text/spreadsheet", /^x-fmt\/106( |$)/,

		// app specific
		"BiPlane spreadsheet"
	];
	converters     = ["soffice[format:SYLK]", "excel97"];
}

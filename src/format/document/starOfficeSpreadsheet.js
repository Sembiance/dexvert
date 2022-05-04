import {Format} from "../../Format.js";

export class starOfficeSpreadsheet extends Format
{
	name           = "StarOffice Spreadsheet";
	website        = "http://fileformats.archiveteam.org/wiki/SDC";
	ext            = [".sdc", ".stc", ".sxc", ".vor"];
	forbidExtMatch = true;
	magic          = ["StarOffice StarCalc spreadsheet", /^OLE 2 Compound Document.* StarCalc.* spreadsheet/, "StarOffice Calc spreadsheet", /^x-fmt\/359( |$)/];
	converters     = ["soffice"];
}

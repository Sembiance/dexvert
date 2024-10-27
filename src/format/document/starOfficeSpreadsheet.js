import {Format} from "../../Format.js";

export class starOfficeSpreadsheet extends Format
{
	name           = "StarOffice Spreadsheet";
	website        = "http://fileformats.archiveteam.org/wiki/SDC";
	ext            = [".sdc", ".stc", ".sxc", ".vor"];
	forbidExtMatch = true;
	magic          = ["StarOffice StarCalc spreadsheet", /^OLE 2 Compound Document.* StarCalc.* spreadsheet/, "StarOffice Calc spreadsheet", "application/vnd.sun.xml.calc", /^fmt\/(808|809)( |$)/, /^x-fmt\/359( |$)/];
	converters     = ["soffice[format:StarOffice Spreadsheet]"];
}

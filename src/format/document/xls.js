import {Format} from "../../Format.js";

export class xls extends Format
{
	name       = "Excel Spreadsheet";
	website    = "http://fileformats.archiveteam.org/wiki/XLS";
	ext        = [".xls", ".xlsx"];
	magic      = ["Microsoft Excel worksheet", "Microsoft Excel for OS/2 worksheet", "Microsoft Excel sheet", "Excel Microsoft Office Open XML Format document"];
	converters = ["soffice[matchType:magic]", "antixls"];
}

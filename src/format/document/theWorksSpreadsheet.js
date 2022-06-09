import {Format} from "../../Format.js";

export class theWorksSpreadsheet extends Format
{
	name           = "The Works! Spreadsheet";
	ext            = [".sht"];
	forbidExtMatch = true;
	magic          = ["The Works! Spreadsheet"];
	converters     = ["strings"];
}

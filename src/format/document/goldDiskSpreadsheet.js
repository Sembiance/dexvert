import {Format} from "../../Format.js";

export class goldDiskSpreadsheet extends Format
{
	name           = "Gold Disk Spreadsheet";
	ext            = [".adv", ".pcf"];
	forbidExtMatch = true;
	magic          = ["Gold Disk Office Calc/Graph spreadsheet"];
	converters     = ["strings"];
}

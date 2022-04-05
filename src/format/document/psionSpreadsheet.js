import {Format} from "../../Format.js";

export class psionSpreadsheet extends Format
{
	name           = "Psion Spreadsheet";
	ext            = [".spr"];
	forbidExtMatch = true;
	magic          = ["Psion SH3 Spreadsheet"];
	converters     = ["strings"];
}

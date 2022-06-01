import {Format} from "../../Format.js";

export class wingzSpreadsheet extends Format
{
	name           = "Wingz Spreadsheet";
	ext            = [".wkz"];
	forbidExtMatch = true;
	magic          = ["Wingz spreadsheet"];
	converters     = ["strings"];
}

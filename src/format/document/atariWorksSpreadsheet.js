import {Format} from "../../Format.js";

export class atariWorksSpreadsheet extends Format
{
	name           = "Atari Works Spreadsheet";
	ext            = [".sts"];
	forbidExtMatch = true;
	magic          = ["Atari Works Spreadsheet"];
	converters     = ["strings"];
}

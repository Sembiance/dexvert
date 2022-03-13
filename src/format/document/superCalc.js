import {Format} from "../../Format.js";

export class superCalc extends Format
{
	name           = "SuperCalc Worksheet";
	ext            = [".cal"];
	forbidExtMatch = true;
	magic          = ["SuperCalc worksheet", "SuperCalc 2/3 spreadsheet"];
	converters     = ["strings"];
}

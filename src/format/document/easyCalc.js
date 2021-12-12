import {Format} from "../../Format.js";

export class easyCalc extends Format
{
	name           = "EasyCalc Spreadsheet file";
	ext            = [".calc"];
	forbidExtMatch = true;
	magic          = ["EasyCalc spreadsheet"];
	converters     = ["strings"];
}

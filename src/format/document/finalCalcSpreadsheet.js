import {Format} from "../../Format.js";

export class finalCalcSpreadsheet extends Format
{
	name        = "FinalCalc Spreadsheet";
	ext         = [".sheet"];
	magic       = ["FinalCalc spreadsheet"];
	unsupported = true;
}

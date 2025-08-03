import {Format} from "../../Format.js";

export class sbigCCDOPS extends Format
{
	name           = "SBIG CCDOPS Image";
	ext            = [".stx", ".st4", ".st7", ".sbig"];
	forbidExtMatch = true;
	magic          = ["SBIG CCD ST-7/Standard Image :stx:"];
	converters     = ["nconvert[format:stx]"];
}

import {Format} from "../../Format.js";

export class rdosRawOPL extends Format
{
	name           = "Rdos Raw OPL";
	ext            = [".raw", ".rac"];
	forbidExtMatch = [".raw"];
	magic          = ["RdosPlay RAW", "Rdos Raw OPL Capture music"];
	metaProvider   = ["musicInfo"];
	converters     = ["adplay"];
}

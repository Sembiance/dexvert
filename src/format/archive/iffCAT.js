import {Format} from "../../Format.js";

export class iffCAT extends Format
{
	name           = "IFF CAT file";
	ext            = [".iff"];
	forbidExtMatch = true;
	magic          = [
		// generic
		"IFF CAT file",
		
		// specific
		"Kindwords document (v2.x)", "TrapFAX FAX"
	];
	trustMagic     = true;
	converters     = ["iffCATExtract"];
}

import {Format} from "../../Format.js";

export class iffCAT extends Format
{
	name           = "IFF CAT file";
	ext            = [".iff"];
	forbidExtMatch = true;
	magic          = ["IFF CAT file", "Kindwords document (v2.x)"];
	trustMagic     = true;
	converters     = ["iffCATExtract"];
}

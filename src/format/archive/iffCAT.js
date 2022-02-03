import {Format} from "../../Format.js";

export class iffCAT extends Format
{
	name           = "IFF CAT file";
	ext            = [".iff"];
	forbidExtMatch = true;
	magic          = ["IFF CAT file"];
	trustMagic     = true;
	converters     = ["iffCATExtract"];
}

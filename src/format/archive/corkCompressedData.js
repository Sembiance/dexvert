import {Format} from "../../Format.js";

export class corkCompressedData extends Format
{
	name           = "Cork compressed data";
	ext            = ["$"];
	forbidExtMatch = true;
	magic          = ["Cork compressed data", "deark: cork"];
	converters     = ["deark[module:cork]"];
}

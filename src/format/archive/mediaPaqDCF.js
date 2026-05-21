import {Format} from "../../Format.js";

export class mediaPaqDCF extends Format
{
	name           = "MediaPaq DCF Catalog";
	ext            = [".dcf"];
	forbidExtMatch = true;
	magic          = ["DCF images container"];
	converters     = ["vibeExtract"];
}

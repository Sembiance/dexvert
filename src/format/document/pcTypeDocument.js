import {Format} from "../../Format.js";

export class pcTypeDocument extends Format
{
	name           = "PC-Type Document";
	ext            = [".pct"];
	forbidExtMatch = true;
	magic          = ["PC-Type document"];
	converters     = ["strings"];
}

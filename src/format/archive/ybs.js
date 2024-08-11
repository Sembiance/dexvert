import {Format} from "../../Format.js";

export class ybs extends Format
{
	name           = "YBS Archive";
	ext            = [".ybs"];
	forbidExtMatch = true;
	magic          = [/^Ybs archive data/, "YBS compressed archive"];
	converters     = ["ybs"];
}

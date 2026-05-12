import {Format} from "../../Format.js";

export class acgMovie extends Format
{
	name           = "ACG Movie";
	ext            = [".wdf", ".m24"];
	forbidExtMatch = true;
	magic          = ["ACG Movie"];
	converters     = ["na_eofdec"];
}

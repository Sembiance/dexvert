import {Format} from "../../Format.js";

export class theatrixWMO extends Format
{
	name           = "Theatrix WMO";
	ext            = [".wmo", ".mov"];
	forbidExtMatch = true;
	magic          = ["Theatrix WMO"];
	converters     = ["na_eofdec[format:wmo]"];
}

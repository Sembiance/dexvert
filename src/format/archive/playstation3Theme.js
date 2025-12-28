import {Format} from "../../Format.js";

export class playstation3Theme extends Format
{
	name           = "PlayStation 3 Theme";
	ext            = [".p3t"];
	forbidExtMatch = true;
	magic          = ["PlayStation 3 Theme"];
	converters     = ["p3t_extract"];
}

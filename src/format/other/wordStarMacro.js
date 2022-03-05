import {Format} from "../../Format.js";

export class wordStarMacro extends Format
{
	name           = "WordStar Macro";
	ext            = [".wsm"];
	forbidExtMatch = true;
	magic          = ["WordStar Macro"];
	converters     = ["strings"];
}

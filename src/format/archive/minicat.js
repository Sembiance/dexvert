import {Format} from "../../Format.js";

export class minicat extends Format
{
	name           = "MINICAT Archive";
	ext            = [".cat"];
	forbidExtMatch = true;
	magic          = ["MINICAT Archive"];
	converters     = ["foremost"];
}

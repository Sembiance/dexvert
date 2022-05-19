import {Format} from "../../Format.js";

export class annaMarie extends Format
{
	name           = "Anna-Marie Archive";
	ext            = [".dat"];
	forbidExtMatch = true;
	magic          = ["Anna-Marie Archive"];
	converters     = ["foremost"];
}

import {Format} from "../../Format.js";

export class canDoVariables extends Format
{
	name           = "CanDo Variables/Data";
	ext            = [".var", ".data"];
	forbidExtMatch = true;
	magic          = ["CanDo Variables/data container"];
	converters     = ["strings"];
}

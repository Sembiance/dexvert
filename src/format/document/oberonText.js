import {Format} from "../../Format.js";

export class oberonText extends Format
{
	name           = "Oberon Text";
	ext            = [".mod"];
	forbidExtMatch = true;
	magic          = ["Oberon V4 text format"];
	converters     = ["strings"];
}

import {Format} from "../../Format.js";

export class newAgeHelp extends Format
{
	name           = "NewAge Help";
	ext            = [".hlp"];
	forbidExtMatch = true;
	magic          = ["NewAge Help"];
	converters     = ["strings"];
}

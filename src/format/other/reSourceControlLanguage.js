import {Format} from "../../Format.js";

export class reSourceControlLanguage extends Format
{
	name           = "ReSource Control Language";
	ext            = [".rcl"];
	forbidExtMatch = true;
	magic          = ["ReSource Control Language"];
	weakMagic      = true;
	converters     = ["strings"];
}

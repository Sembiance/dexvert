import {Format} from "../../Format.js";

export class turboCConfiguration extends Format
{
	name           = "Turbo C Configuration";
	ext            = [".tc"];
	forbidExtMatch = true;
	magic          = ["Turbo C Configuration"];
	converters     = ["strings"];
}

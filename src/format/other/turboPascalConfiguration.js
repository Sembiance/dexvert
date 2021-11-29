import {Format} from "../../Format.js";

export class turboPascalConfiguration extends Format
{
	name           = "Turbo Pascal Configuration File";
	ext            = [".tp"];
	forbidExtMatch = true;
	magic          = ["Turbo Pascal configuration"];
	converters     = ["strings"];
}

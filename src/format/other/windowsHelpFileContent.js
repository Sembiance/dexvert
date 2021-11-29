import {Format} from "../../Format.js";

export class windowsHelpFileContent extends Format
{
	name           = "Microsoft Windows Help File Content";
	ext            = [".cnt"];
	forbidExtMatch = true;
	magic          = ["Help File Contents", "MS Windows help file Content"];
	converters     = ["strings"];
}

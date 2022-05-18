import {Format} from "../../Format.js";

export class hyperTextVSUM extends Format
{
	name           = "HyperText VSUM";
	ext            = [".xdb"];
	forbidExtMatch = true;
	magic          = ["HyperText VSUM"];
	converters     = ["strings"];
}

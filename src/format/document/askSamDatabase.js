import {Format} from "../../Format.js";

export class askSamDatabase extends Format
{
	name           = "askSam Database";
	ext            = [".ask"];
	forbidExtMatch = true;
	magic          = ["askSam database", "askSam Windows database"];
	converters     = ["strings"];
}

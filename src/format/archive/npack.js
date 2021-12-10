import {Format} from "../../Format.js";

export class npack extends Format
{
	name           = "NPack Archive";
	website        = "http://fileformats.archiveteam.org/wiki/NPack";
	ext            = [".$"];
	forbidExtMatch = true;
	magic          = ["NPack archive data"];
	converters     = ["npack"];
}

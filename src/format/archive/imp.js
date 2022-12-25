import {Format} from "../../Format.js";

export class imp extends Format
{
	name           = "IMP";
	website        = "http://fileformats.archiveteam.org/wiki/IMP";
	ext            = [".imp"];
	forbidExtMatch = true;
	magic          = ["IMP archive data", "Imp compressed archive"];
	converters     = ["imp"];
}

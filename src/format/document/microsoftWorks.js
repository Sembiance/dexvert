import {Format} from "../../Format.js";

export class microsoftWorks extends Format
{
	name           = "Microsoft Works Document";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Works";
	ext            = [".wps", ".wp", ".doc"];
	forbidExtMatch = true;
	magic          = ["Microsoft Works", "Composite Document File"];
	weakMagic      = true;
	converters     = ["fileMerlin[type:MSWKW*]", "soffice"];
}

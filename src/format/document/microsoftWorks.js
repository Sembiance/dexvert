import {Format} from "../../Format.js";

export class microsoftWorks extends Format
{
	name           = "Microsoft Works Document";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_Works";
	ext            = [".wps", ".wp", ".doc"];
	forbidExtMatch = true;
	magic          = ["Microsoft Works", "Composite Document File"];
	weakMagic      = ["Composite Document File", "Microsoft Works"];
	converters     = ["fileMerlin[type:MSWKW*]", "soffice"];
}

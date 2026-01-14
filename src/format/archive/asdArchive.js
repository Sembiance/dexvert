import {Format} from "../../Format.js";

export class asdArchive extends Format
{
	name           = "ASD Archive";
	website        = "http://fileformats.archiveteam.org/wiki/ASD_Archiver";
	ext            = [".asd"];
	forbidExtMatch = true;
	magic          = ["ASD Archiever compressed archive", "ASD Archiv gefunden", /^ASD archive data/];
	weakMagic      = [/^ASD archive data/, "ASD Archiv gefunden"];
	converters     = ["unasd"];
}

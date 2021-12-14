import {Format} from "../../Format.js";

export class os2Message extends Format
{
	name           = "OS/2 Message File";
	website        = "http://fileformats.archiveteam.org/wiki/MSG_(OS/2)";
	ext            = [".msg"];
	forbidExtMatch = true;
	magic          = [/^OS\/2 help [Mm]essage/];
	converters     = ["strings"];
}

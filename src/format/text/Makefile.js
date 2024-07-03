import {Format} from "../../Format.js";

export class Makefile extends Format
{
	name           = "Makefile";
	website        = "http://fileformats.archiveteam.org/wiki/Makefile";
	ext            = [".mak", ".mk"];
	forbidExtMatch = true;
	filename       = [/^[Mm]ake[Ff]ile[._-].*/, /^[Mm]ake[Ff]ile$/, /.*[Mm]ake[Ff]ile$/];
	magic          = ["makefile script", "automake makefile script"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}

import {Format} from "../../Format.js";

export class pl extends Format
{
	name           = "Perl Script";
	website        = "http://fileformats.archiveteam.org/wiki/Perl";
	ext            = [".pl"];
	forbidExtMatch = true;
	magic          = ["Perl script", /^Perl\d module source/];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}

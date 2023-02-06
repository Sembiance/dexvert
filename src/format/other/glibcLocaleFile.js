import {Format} from "../../Format.js";

export class glibcLocaleFile extends Format
{
	name        = "glibc Locale File";
	website     = "http://fileformats.archiveteam.org/wiki/Microsoft_Agent_character";
	filename    = [/^LC_.+$/];
	magic       = ["glibc locale file LC_"];
	weakMagic   = true;
	unsupported = true;
}

import {Format} from "../../Format.js";

export class windowsFont extends Format
{
	name        = "Windows Font";
	website     = "http://fileformats.archiveteam.org/wiki/FNT_(Windows_Font)";
	ext         = [".fnt"];
	magic       = ["Windows Font resource"];
	weakMagic   = true;
	unsupported = true;
	notes       = "Rumor has it Fony supports bitmap fonts, but I know it doesn't support vector ones like ROMAN.fnt";
}

import {Format} from "../../Format.js";

export class windowsFont extends Format
{
	name           = "Windows Font";
	website        = "http://fileformats.archiveteam.org/wiki/FNT_(Windows_Font)";
	ext            = [".fnt"];
	forbidExtMatch = true;
	magic          = ["Bitstream Font", "Windows Font resource"];
	weakMagic      = ["Windows Font resource"];
	notes          = "Rumor has it Fony supports bitmap fonts, but I know it doesn't support vector ones like ROMAN.fnt and MODERN.fnt";
	converters     = ["deark[module:fnt]"];	// deark doesn't support vector fonts
}

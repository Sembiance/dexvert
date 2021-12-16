import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class asm extends Format
{
	name           = "Assembly Source File";
	website        = "http://fileformats.archiveteam.org/wiki/Assembly_language";
	ext            = [".asm"];
	forbidExtMatch = true;
	magic          = [...TEXT_MAGIC, "C source"];	// file often confuses assembly for C source and nothing else identifies it
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}

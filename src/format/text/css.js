import {Format} from "../../Format.js";
import {TEXT_MAGIC} from "../../Detection.js";

export class css extends Format
{
	name           = "Cascading Style Sheet File";
	website        = "http://fileformats.archiveteam.org/wiki/CSS";
	ext            = [".css"];
	mimeType       = "text/css";
	forbidExtMatch = true;
	magic          = [...TEXT_MAGIC, "assembler source"];	// Sadly file often detects it as assembler source and no other indentifiers come back with magic
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}

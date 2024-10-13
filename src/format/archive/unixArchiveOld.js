import {Format} from "../../Format.js";

export class unixArchiveOld extends Format
{
	name           = "Unix Archive - Old";
	ext            = [".a"];
	forbidExtMatch = true;
	magic          = [/old (16|32)-bit-int (little|big)-endian archive/, "HP old archive"];
	weakMagic      = true;
	unsupported    = true;
}

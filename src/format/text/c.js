import {Format} from "../../Format.js";

export class c extends Format
{
	name           = "C/C++ Source or Header";
	website        = "http://fileformats.archiveteam.org/wiki/C";
	ext            = [".c", ".h", ".cpp", ".cxx", ".cc", ".c++", ".hpp"];
	forbidExtMatch = true;
	filename       = [/source/];
	weakFilename   = true;
	magic          = ["C source", "C++ source"];
	weakMagic      = true;
	untouched      = true;
	metaProvider   = ["text"];
}

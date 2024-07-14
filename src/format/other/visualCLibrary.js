import {Format} from "../../Format.js";

export class visualCLibrary extends Format
{
	name           = "Microsoft Visual C/Basic Library";
	ext            = [".lib"];
	forbidExtMatch = true;
	magic          = [
		"Microsoft Visual C Library", "Microsoft Visual C/OMF library", "C++ Bibliotheks Datei", "Microsoft Basic 7.x compiled library", "Microsoft Basic compiled library", "Microsoft VBDOS 1.00 compiled library"
	];
	unsupported    = true;
}

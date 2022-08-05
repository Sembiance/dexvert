import {xu} from "xu";
import {Format} from "../../Format.js";

export class oricTape extends Format
{
	name        = "ORIC Tape Image";
	website     = "http://fileformats.archiveteam.org/wiki/TAP_(Oric)";
	ext         = [".dat", ".tap"];
	magic       = ["Oric Tape image", "Oric tape"];
	weakMagic   = true;
	unsupported = true;
}

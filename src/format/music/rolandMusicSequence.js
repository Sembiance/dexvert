import {Format} from "../../Format.js";

export class rolandMusicSequence extends Format
{
	name        = "Roland Music Sequence";
	ext         = [".svq"];
	magic       = ["Roland XP-50 music sequence", "Roland music sequence (generic)"];
	weakMagic   = ["Roland music sequence (generic)"];
	notes       = "Awave Studio claims support for these, but I was not able to get it to convert any SVQ files.";
	unsupported = true;
}

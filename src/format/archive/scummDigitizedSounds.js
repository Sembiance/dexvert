import {Format} from "../../Format.js";

export class scummDigitizedSounds extends Format
{
	name       = "SCUMM digitized Sounds";
	website    = "https://wiki.scummvm.org/index.php/SCUMM/Technical_Reference/Sound_resources";
	ext        = [".sou"];
	magic      = ["SCUMM digitized Sounds (v5-6)"];
	converters = ["gameextractor"];
}

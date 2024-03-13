import {Format} from "../../Format.js";

export class octalyser extends Format
{
	name           = "Octalyser Module";
	ext            = [".mod"];
	weakExt        = [".mod"];	// too generic, let mod/soundTracker grab it
	magic          = [/^Octalyser \d-channel STe\/Falcon Module$/, "8-channel Octalyser module"];
	metaProvider   = ["musicInfo"];
	converters     = ["xmp", "zxtune123", "openmpt123"];
}


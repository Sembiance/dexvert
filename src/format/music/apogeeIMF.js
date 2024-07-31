import {Format} from "../../Format.js";

export class apogeeIMF extends Format
{
	name         = "Apogee IMF";
	website      = "http://fileformats.archiveteam.org/wiki/Id_Software_Music_Format";
	ext          = [".imf"];
	metaProvider = ["musicInfo"];
	converters   = ["adplay", "gamemus"];
}

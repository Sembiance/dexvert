import {Format} from "../../Format.js";

export class ay extends Format
{
	name         = "AY Amadeus Chiptune";
	website      = "http://fileformats.archiveteam.org/wiki/AY";
	ext          = [".ay", ".emul"];
	magic        = ["Spectrum 128 tune", "AY chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

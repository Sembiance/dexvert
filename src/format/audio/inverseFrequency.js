import {Format} from "../../Format.js";

export class inverseFrequency extends Format
{
	name        = "Inverse Frequency Sound Format";
	website     = "http://fileformats.archiveteam.org/wiki/Inverse_Frequency_Sound_format";
	magic       = ["Inverse Frequency Sound format"];
	unsupported = true;
	notes       = "Used in various APOGEE games like commander keen. Didn't look that hard for a player/converter.";
}

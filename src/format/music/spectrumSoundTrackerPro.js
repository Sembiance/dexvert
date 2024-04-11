import {Format} from "../../Format.js";

export class spectrumSoundTrackerPro extends Format
{
	name         = "Spectrum Sound Tracker Pro";
	ext          = [".stp", ".stp2"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul"];
}

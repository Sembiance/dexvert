import {Format} from "../../Format.js";

export class spectrumSoundTracker extends Format
{
	name         = "Spectrum Sound Tracker";
	ext          = [".st11", ".st13"];
	magic        = [/^Spectrum Sound Tracker .*chiptune$/];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

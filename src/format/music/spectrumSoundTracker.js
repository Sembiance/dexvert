import {Format} from "../../Format.js";

export class spectrumSoundTracker extends Format
{
	name         = "Spectrum Sound Tracker";
	ext          = [".st1", ".st3", ".stc"];
	magic        = [/^Spectrum Sound Tracker .*chiptune$/];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
}

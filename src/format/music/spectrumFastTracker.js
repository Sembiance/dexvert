import {Format} from "../../Format.js";

export class spectrumFastTracker extends Format
{
	name         = "Spectrum Fast Tracker";
	ext          = [".ftc"];
	magic        = ["Spectrum Fast Tracker chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul"];
}

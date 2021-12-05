import {Format} from "../../Format.js";

export class soundBlasterInstrument extends Format
{
	name        = "Sound Blaster Instrument";
	website     = "http://fileformats.archiveteam.org/wiki/Sound_Blaster_Instrument";
	ext         = [".sbi"];
	magic       = ["SoundBlaster instrument data", "Sound Blaster Instrument audio"];
	unsupported = true;
}

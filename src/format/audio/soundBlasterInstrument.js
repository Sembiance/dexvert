import {Format} from "../../Format.js";

export class soundBlasterInstrument extends Format
{
	name           = "Sound Blaster Instrument";
	website        = "http://fileformats.archiveteam.org/wiki/Sound_Blaster_Instrument";
	ext            = [".sbo", ".sb", ".dat"];
	forbidExtMatch = true;
	magic          = ["SoundBlaster instrument data", "Sound Blaster Instrument audio", "SoundBlaster Instrument Patch"];
	weakMagic      = ["SoundBlaster instrument data", "Sound Blaster Instrument audio"];
	converters     = ["vibe2wav"];
}

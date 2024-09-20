import {Format} from "../../Format.js";

export class eXtendedInstrument extends Format
{
	name           = "eXtended Instrument";
	website        = "http://fileformats.archiveteam.org/wiki/Extended_instrument";
	ext            = [".xi"];
	forbidExtMatch = true;
	magic          = ["eXtended Instrument", "Fast Tracker II Instrument", "audio/x-xi"];
	converters     = ["awaveStudio"];
}

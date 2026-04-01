import {Format} from "../../Format.js";

export class musiclineInstrument extends Format
{
	name        = "Musicline Instrument";
	website     = "https://www.musicline.org/";
	magic       = ["Musicline instrument"];
	unsupported = true;	// only 7 unique files on discmaster, all less than 700 bytes
}

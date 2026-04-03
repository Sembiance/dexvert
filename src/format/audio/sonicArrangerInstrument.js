import {Format} from "../../Format.js";

export class sonicArrangerInstrument extends Format
{
	name        = "Sonic Arranger instrument";
	magic       = ["Sonic Arranger instrument"];
	fileSize    = 672;
	unsupported = true;	// only 43 unique files on discmaster, all only 672 bytes so not likely to be interesting
	notes       = "No known converter";
}

import {Format} from "../../Format.js";

export class artOfNoiseInstrument extends Format
{
	name        = "Art of Noise Instrument";
	ext         = [".fm"];
	magic       = ["Art Of Noise MF instrument"];
	unsupported = true;	// only 85 samples on discmaster, all but one of them are only 24 bytes
}

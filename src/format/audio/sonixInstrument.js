import {xu} from "xu";
import {Format} from "../../Format.js";

export class sonixInstrument extends Format
{
	name        = "Aegis Sonix Instrument";
	ext         = [".instr"];
	magic       = ["Sonix sampled sound Instrument", "Sonix synthesised Instrument"];
	weakMagic   = true;
	unsupported = true;
	notes       = xu.trim`
		The sampled .instr files appear to be 'meta' files that usually point to the .ss files which seems to contain the sampled sounds.
		These files are used as the instruments in .smus files.
		In theory I should be able to convert these instruments into .wav's as a sound for each instrument/.ss file.
		Some of these are actuall "sonix" files, but other .instr files are more generic, like IFF generic`;
}

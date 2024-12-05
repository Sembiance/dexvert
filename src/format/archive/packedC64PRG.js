import {Format} from "../../Format.js";

export class packedC64PRG extends Format
{
	name           = "Packed C64 PRG";
	magic          = ["P64 ", "8bit C64 executable Pu-Crunch compressed", /^Commodore C64 program, probably PUCrunch archive data/];
	forbiddenMagic = [
		"P64 Guessed", "P64 NRZI flux pulse disk image",
		
		// infinite loops
		"P64 TBC Multicompactor",	// archive/packedC64PRG/happy birthday
		"P64 CruelCrunch"			// archive/packedC64PRG/turrican part 2_
	];
	priority       = this.PRIORITY.LOWEST;
	converters     = ["unp64"];
}

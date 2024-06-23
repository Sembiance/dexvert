import {Format} from "../../Format.js";

export class packedC64PRG extends Format
{
	name           = "Packed C64 PRG";
	magic          = ["P64 "];
	forbiddenMagic = ["P64 Guessed", "P64 NRZI flux pulse disk image"];
	priority       = this.PRIORITY.LOWEST;
	converters     = ["unp64"];
}

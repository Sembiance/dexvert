import {Format} from "../../Format.js";

export class packedC64PRG extends Format
{
	name           = "Packed C64 PRG";
	magic          = ["P64 "];
	forbiddenMagic = ["P64 NRZI flux pulse disk image"];
	converters     = ["unp64"];
}

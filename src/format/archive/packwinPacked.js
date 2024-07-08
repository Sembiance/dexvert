import {Format} from "../../Format.js";

export class packwinPacked extends Format
{
	name       = "PACKWIN Packed";
	magic      = ["16bit DOS EXE PACKWIN compressed"];
	packed     = true;
	converters = ["unp", "cup386"];
}

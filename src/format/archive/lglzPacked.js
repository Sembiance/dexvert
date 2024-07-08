import {Format} from "../../Format.js";

export class lglzPacked extends Format
{
	name       = "LGLZ Packed";
	magic      = ["16bit DOS EXE LGLZ compressed"];
	packed     = true;
	converters = ["cup386"];
}

import {Format} from "../../Format.js";

export class tinyProgPacked extends Format
{
	name       = "TinyProg Packed";
	magic      = ["16bit DOS EXE TinyProg compressed"];
	packed     = true;
	converters = ["unp"];
}

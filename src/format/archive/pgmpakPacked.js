import {Format} from "../../Format.js";

export class pgmpakPacked extends Format
{
	name       = "PGMPAK Packed";
	magic      = ["16bit DOS EXE PGMPAK compressed"];
	packed     = true;
	converters = ["unp"];
}

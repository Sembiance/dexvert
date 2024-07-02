import {Format} from "../../Format.js";

export class wwpackPacked extends Format
{
	name       = "WWPACK Packed";
	magic      = ["16bit DOS EXE WWPACK compressed"];
	packed     = true;
	converters = ["unp", "cup386"];
}

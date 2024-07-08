import {Format} from "../../Format.js";

export class cruncherPacked extends Format
{
	name       = "Cruncher Packed";
	magic      = ["Cruncher compressed DOS executable"];
	packed     = true;
	converters = ["cup386"];
}

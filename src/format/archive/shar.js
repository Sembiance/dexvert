import {Format} from "../../Format.js";

export class shar extends Format
{
	name       = "SHell self-extracting ARchive";
	website    = "http://fileformats.archiveteam.org/wiki/Shar";
	ext        = [".shar", ".sha"];
	magic      = ["shell archive text", "shar SHell self-extracting aRchive"];
	converters = ["unshar"];
}

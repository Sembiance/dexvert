import {Format} from "../../Format.js";

export class lzexePacked extends Format
{
	name       = "LZEXE Packed";
	website    = "http://fileformats.archiveteam.org/wiki/LZEXE";
	magic      = ["Packer: LZEXE", "LZEXE compressed DOS executable"];
	packed     = true;
	converters = ["deark[module:lzexe]"];
}

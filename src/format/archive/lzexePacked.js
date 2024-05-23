import {Format} from "../../Format.js";

export class lzexePacked extends Format
{
	name       = "LZEXE Packed";
	website    = "http://fileformats.archiveteam.org/wiki/LZEXE";
	magic      = ["Packer: LZEXE"];
	packed     = true;
	converters = ["deark[module:lzexe]"];
}

import {Format} from "../../Format.js";

export class pklitePacked extends Format
{
	name       = "PKLITE Packed";
	website    = "http://fileformats.archiveteam.org/wiki/PKLITE";
	magic      = ["Packer: PKLITE"];
	packed     = true;
	converters = ["deark[module:pklite]"];
}

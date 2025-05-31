import {Format} from "../../Format.js";

export class pklitePacked extends Format
{
	name       = "PKLITE Packed";
	website    = "http://fileformats.archiveteam.org/wiki/PKLITE";
	magic      = ["Packer: PKLITE", "16bit DOS EXE PKLite compressed", "deark: pklite (PKLITE-compressed"];
	packed     = true;
	converters = ["deark[module:pklite]"];
}

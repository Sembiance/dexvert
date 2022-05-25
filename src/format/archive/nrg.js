import {Format} from "../../Format.js";

export class nrg extends Format
{
	name       = "Nero CD Image";
	website    = "http://fileformats.archiveteam.org/wiki/NRG";
	ext        = [".nrg"];
	magic      = ["Nero CD image"];
	priority   = this.PRIORITY.TOP;	// NRG is often mis-identified as ISO
	
	// According to nrg2iso we just skip the first 307,200 bytes: http://gregory.kokanosky.free.fr/v4/linux/nrg2iso.en.html
	converters = ["dd[bs:307200][skip:1] -> dexvert", "iat", "UniExtract"];
}

import {Format} from "../../Format.js";

export class hiPic extends Format
{
	name       = "Hi-Pic Creator";
	website    = "http://fileformats.archiveteam.org/wiki/Hi-Pic_Creator";
	ext        = [".hpc"];
	magic      = ["Koala Paint"];	// Shares the same magic
	weakMagic  = true;
	trustMagic = true;	// Koala Paint is normally untrustworthy, but we trust it here
	fileSize   = 9003;
	converters = ["recoil2png"]
}

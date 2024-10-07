import {Format} from "../../Format.js";

export class zxMonochrome extends Format
{
	name       = "ZX Monochrome";
	website    = "http://fileformats.archiveteam.org/wiki/SCR_(ZX_Spectrum)";
	ext        = [".scr"];
	fileSize   = 6144;
	idCheck    = inputFile => !["ediicon", "errorbox", "f83-ovl", "figed", "lmi-ovl", "mvp-ovl", "pcf-ovl", "uni-ovl"].includes(inputFile.name.toLowerCase());	// These are false positives that recur in the wild
	converters = ["recoil2png"];
}

import {Format} from "../../Format.js";

export class stx extends Format
{
	name       = "PASTI Disk Image";
	website    = "http://fileformats.archiveteam.org/wiki/STX";
	ext        = [".stx"];
	magic      = ["PASTI disk image", "application/x-stx-disk-image"];
	converters = ["deark[module:pasti]"];
}

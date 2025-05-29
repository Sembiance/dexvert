import {Format} from "../../Format.js";

export class grub2PFF2 extends Format
{
	name       = "GRUB 2 PFF2 Font";
	website    = "http://fileformats.archiveteam.org/wiki/PFF2";
	ext        = [".pf2"];
	magic      = ["GRUB2 font", "deark: pff2"];
	converters = ["deark[module:pff2]"];
}

import {Format} from "../../Format.js";

export class xRes extends Format
{
	name        = "xRes Image";
	website     = "http://fileformats.archiveteam.org/wiki/XRes";
	ext         = [".lrg"];
	magic       = ["xRes multi-resolution bitmap"];
	notes       = "Have xRes 3.0 in sandbox/app but even though it installed in both Win2k and WinXP it doesn't launch, just exits. Could try with Vista or maybe it's a lost cause. Only encountered on 1 CD so far.";
	unsupported = true;
}

import {Format} from "../../Format.js";

export class ntitler extends Format
{
	name        = "NTitler Animation";
	ext         = [".nt"];
	magic       = ["NTitler show"];
	unsupported = true;	// only 88 unique files on discmaster, all very small (most <1k), thus not gonna be very interesting
	notes       = "Couldn't locate a converter or extractor. Original Amiga program is here: http://aminet.net/package/gfx/misc/ntpro";
}

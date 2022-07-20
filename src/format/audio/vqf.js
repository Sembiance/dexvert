import {Format} from "../../Format.js";

export class vqf extends Format
{
	name        = "VQF TwinVQ";
	website     = "https://wiki.multimedia.cx/index.php/VQF";
	ext         = [".vqf"];
	magic       = ["VQF data", "TwinVQF audio"];
	unsupported = true;
	notes       = "I attempted to use TwinDec from http://www.rarewares.org/rrw/nttvqf.php but it failed to decode my sample files";
}

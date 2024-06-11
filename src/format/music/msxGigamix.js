import {Format} from "../../Format.js";

export class msxGigamix extends Format
{
	name       = "MSX Gigamix Music";
	ext        = [".mgs"];
	magic      = ["MSX Gigamix"];
	weakMagic  = true;
	converters = ["kss2wav"];
}

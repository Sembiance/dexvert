import {Format} from "../../Format.js";

export class ariaSamplesBank extends Format
{
	name        = "ARIA Samples Bank";
	ext         = [".bnk"];
	magic       = ["ARIA samples Bank"];
	unsupported = true;	// only 9 unique samples on discmaster, all less than 24k, so likely no audio within
}

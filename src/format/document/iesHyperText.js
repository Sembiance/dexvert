import {Format} from "../../Format.js";

export class iesHyperText extends Format
{
	name        = "I.E.S. HyperText";
	ext         = [".hyp"];
	magic       = ["I.E.S. HyperText"];
	unsupported = true;	// only 40 unique files on discmaster
}

import {Format} from "../../Format.js";

export class iffCMUS extends Format
{
	name           = "DeLuxe Music CMUS";
	ext            = [".dmcs", ".iff"];
	forbidExtMatch = [".iff"];
	magic          = ["IFF data, CMUS complex music", "IFF Common Musical Score"];
	unsupported    = true;	// only 77 unique files on discmaster, but several probably false positives, so likely less
}

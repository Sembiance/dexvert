import {Format} from "../../Format.js";

export class iffCMUS extends Format
{
	name        = "DeLuxe Music CMUS";
	ext         = [".dmcs", ".iff"];
	magic       = ["IFF data, CMUS complex music", "IFF Common Musical Score"];
	unsupported = true;
}

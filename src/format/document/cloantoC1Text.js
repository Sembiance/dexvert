import {Format} from "../../Format.js";

export class cloantoC1Text extends Format
{
	name        = "Cloanto C1-Text Document";
	ext         = [".c1text"];
	magic       = ["Cloanto C1-Text compressed document"];
	unsupported = true;	// only 5 unique files on discmaster
}

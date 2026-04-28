import {Format} from "../../Format.js";

export class alanInteractiveFiction extends Format
{
	name        = "Alan Interactive Fiction";
	ext         = [".acd"];
	magic       = ["Alan 2 Code"];
	unsupported = true;	// only 31 unique files on discmaster, several are just dictionaries
}

import {Format} from "../../Format.js";

export class cazip extends Format
{
	name       = "CAZIP File";
	ext        = [".caz"];
	magic      = ["CAZIP compressed file"];
	converters = ["cazip"];
}


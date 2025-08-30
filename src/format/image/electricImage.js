import {Format} from "../../Format.js";

export class electricImage extends Format
{
	name       = "Electric Image";
	magic      = ["Electric Image :eidi:"];
	converters = ["nconvert[format:eidi]"];
}

import {Format} from "../../Format.js";

export class eroiicaEIF extends Format
{
	name       = "Eroiica EIF";
	magic      = ["Eroiica :eif:"];
	converters = ["nconvert[format:eif]"];
}

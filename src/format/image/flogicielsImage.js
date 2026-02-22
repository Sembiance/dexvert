import {Format} from "../../Format.js";

export class flogicielsImage extends Format
{
	name       = "Flogiciels Image";
	ext        = [".cpt", ".lcr"];
	magic      = ["Flogiciels Image"];
	converters = ["uncryptFlogiciels"];
}

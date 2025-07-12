import {Format} from "../../Format.js";

export class ecchi extends Format
{
	name           = "Ecchi Image";
	ext            = [".ecc"];
	forbidExtMatch = true;
	magic          = ["Ecchi :ecc:"];
	converters     = ["nconvert[format:ecc]"];
}

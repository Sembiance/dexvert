import {Format} from "../../Format.js";

export class ecchi extends Format
{
	name           = "Ecchi Image";
	ext            = [".ecc"];
	forbidExtMatch = true;
	magic          = ["Ecchi :ecc:", "Ecchi ECC animation"];
	converters     = ["nconvert[format:ecc]"];
}

import {Format} from "../../Format.js";

export class tmmFractalVideo extends Format
{
	name           = "TMM Fractal Video";
	ext            = [".xxx"];
	forbidExtMatch = true;
	magic          = ["TMM Fractal Video"];
	converters     = ["na_eofdec[format:tmm-frac]"];
}

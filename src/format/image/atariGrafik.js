import {Format} from "../../Format.js";

export class atariGrafik extends Format
{
	name           = "Atari Grafik";
	ext            = [".pcp"];
	forbidExtMatch = true;
	magic          = ["Atari Grafik :pcp:"];
	converters     = ["nconvert[format:pcp]"];
}

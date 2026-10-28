import {Format} from "../../Format.js";

export class tandyvisionImage extends Format
{
	name           = "Tandyvision Image";
	ext            = [".vga"];
	forbidExtMatch = true;
	magic          = ["Tandyvisionn Image"];
	converters     = ["na_eofdec[format:tandyvid][outType:png]"];
}

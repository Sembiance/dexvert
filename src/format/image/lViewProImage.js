import {Format} from "../../Format.js";

export class lViewProImage extends Format
{
	name           = "LView Pro Image";
	ext            = [".lvp"];
	forbidExtMatch = true;
	magic          = ["LView Pro Image :lvp:"];
	converters     = ["nconvert[format:lvp]"];
}

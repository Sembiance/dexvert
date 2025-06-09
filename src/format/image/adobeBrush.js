import {Format} from "../../Format.js";

export class adobeBrush extends Format
{
	name           = "Adobe Brush";
	ext            = [".abr"];
	forbidExtMatch = true;
	magic          = ["Adobe Brush :abr:"];
	converters     = ["nconvert[format:abr]"];
}

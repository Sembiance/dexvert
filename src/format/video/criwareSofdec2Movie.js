import {Format} from "../../Format.js";

export class criwareSofdec2Movie extends Format
{
	name           = "CRIWARE/Scaleform Sofdec2 Movie";
	ext            = [".usm"];
	forbidExtMatch = true;
	magic          = ["CRIWARE Sofdec2 Movie", "CRI USM (usm)", /^Scaleform video$/];
	converters     = ["vibe2avi"];
}

import {Format} from "../../Format.js";

export class powerPoint extends Format
{
	name           = "Power Point";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_PowerPoint";
	ext            = [".ppt", ".pp"];
	forbidExtMatch = true;
	magic          = ["Microsoft PowerPoint"];
	converters     = ["soffice"];
}

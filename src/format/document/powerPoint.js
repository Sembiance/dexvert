import {Format} from "../../Format.js";

export class powerPoint extends Format
{
	name           = "Power Point";
	website        = "http://fileformats.archiveteam.org/wiki/Microsoft_PowerPoint";
	ext            = [".ppt", ".pp", ".ppsx", ".pptm", ".pptx"];
	forbidExtMatch = true;
	magic          = ["Microsoft PowerPoint", "PowerPoint Microsoft Office Open XML Format document"];
	converters     = ["soffice"];
}

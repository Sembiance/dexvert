import {Format} from "../../Format.js";

export class xara extends Format
{
	name           = "Xara XAR Graphic";
	website        = "http://fileformats.archiveteam.org/wiki/Xar_(vector_graphics)";
	ext            = [".xar", ".web"];
	forbidExtMatch = [".web"];
	magic          = ["Xara graphics file", "Corel Xara Web document", /^fmt\/922( |$)/];
	converters     = ["nconvert", "graphicWorkshopProfessional", "tomsViewer"];
}

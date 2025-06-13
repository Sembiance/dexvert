import {Format} from "../../Format.js";

export class lightWorkImage extends Format
{
	name           = "LightWork Image bitmap";
	website        = "http://fileformats.archiveteam.org/wiki/LightWork_Image";
	ext            = [".lwi"];
	forbidExtMatch = true;
	magic          = ["LightWork Image bitmap", "Light Work Image :lwi:"];
	converters     = ["nconvert[format:lwi]", "wuimg"];
}

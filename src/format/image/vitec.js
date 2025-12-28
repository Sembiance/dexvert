import {Format} from "../../Format.js";

export class vitec extends Format
{
	name           = "VITec Image";
	website        = "http://fileformats.archiveteam.org/wiki/VITec";
	ext            = [".vitec", ".vit"];
	forbidExtMatch = true; // very rare format
	magic          = ["VITec image format bitmap", "deark: vitec"];
	converters     = ["deark[module:vitec]", "imageAlchemy"];
}

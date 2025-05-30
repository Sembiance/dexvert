import {Format} from "../../Format.js";

export class hsiRaw extends Format
{
	name           = "HSI Raw";
	website        = "http://fileformats.archiveteam.org/wiki/HSI_Raw";
	ext            = [".raw", ".hst"];
	forbidExtMatch = [".raw"];
	magic          = ["HSI Raw bitmap", "deark: hsiraw"];
	converters     = ["deark[module:hsiraw]", "nconvert", "imageAlchemy"];
}

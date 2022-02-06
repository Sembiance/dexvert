import {Format} from "../../Format.js";

export class konicaQualityPhoto extends Format
{
	name       = "Konica Quality Photo";
	website    = "http://fileformats.archiveteam.org/wiki/KPQ";
	ext        = [".kqp"];
	magic      = ["Konica Quality Photo"];
	converters = ["deark", "nconvert"];
}

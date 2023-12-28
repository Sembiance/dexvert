import {Format} from "../../Format.js";

export class konicaQualityPhoto extends Format
{
	name       = "Konica Quality Photo";
	website    = "http://fileformats.archiveteam.org/wiki/KQP";
	ext        = [".kqp", ".pic"];
	magic      = ["Konica Quality Photo"];
	converters = ["deark[module:picjpeg]", "nconvert"];
}

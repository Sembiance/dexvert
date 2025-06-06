import {Format} from "../../Format.js";

export class konicaQualityPhoto extends Format
{
	name       = "Konica Quality Photo aka Pegaus PIC";
	website    = "http://fileformats.archiveteam.org/wiki/KQP";
	ext        = [".kqp", ".pic"];
	magic      = ["Konica Quality Photo", "Pegasus PIC bitmap", "deark: picjpeg (Pegasus JPEG or KQP)"];
	converters = ["deark[module:picjpeg]"];
}

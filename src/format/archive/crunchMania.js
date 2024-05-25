import {Format} from "../../Format.js";

export class crunchMania extends Format
{
	name       = "Crunch-Mania Archive";
	ext        = [".crm", ".crm2"];
	website    = "http://fileformats.archiveteam.org/wiki/Crunch-Mania";
	magic      = ["Crunch-Mania compressed data", "CrM2: Crunch-Mania", "CrM!: Crunch-Mania", "Archive: Crunch-Mania"];
	packed     = true;
	converters = ["decrmtool", "ancient", "xfdDecrunch"];
}

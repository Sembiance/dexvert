import {Format} from "../../Format.js";

export class crunchMania extends Format
{
	name       = "Crunch-Mania Archive";
	ext        = [".crm", ".crm2"];
	website    = "http://fileformats.archiveteam.org/wiki/Crunchmania";
	magic      = ["Crunch-Mania compressed data", "CrM2: Crunch-Mania", "CrM!: Crunch-Mania"];
	packed     = true;
	converters = ["decrmtool", "ancient", "xfdDecrunch"];
}

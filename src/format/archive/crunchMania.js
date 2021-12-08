import {Format} from "../../Format.js";

export class crunchMania extends Format
{
	name       = "Crunch-Mania Archive";
	website    = "http://fileformats.archiveteam.org/wiki/Crunchmania";
	magic      = ["Crunch-Mania compressed data"];
	converters = ["decrmtool", "ancient"];
}

import {Format} from "../../Format.js";

export class nlq extends Format
{
	name       = "Daisy-Dot";
	website    = "http://fileformats.archiveteam.org/wiki/Daisy-Dot_font";
	ext        = [".nlq"];
	magic      = ["Daisy-Dot NLQ font", /^fmt\/(1546|1547)( |$)/];
	notes      = "Most of the sample files do not convert with recoil2png. Maybe a different version?";
	converters = ["recoil2png[format:NLQ]"];
}

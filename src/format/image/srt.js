import {Format} from "../../Format.js";

export class srt extends Format
{
	name       = "Synthetic Arts";
	website    = "http://fileformats.archiveteam.org/wiki/Synthetic_Arts";
	ext        = [".srt"];
	fileSize   = 32038;
	converters = ["recoil2png[format:SRT]"];
}

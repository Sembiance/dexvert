import {Format} from "../../Format.js";

export class hancomWord extends Format
{
	name        = "Hancom Word";
	website     = "http://fileformats.archiveteam.org/wiki/HWP";
	ext         = [".hwp"];
	magic       = ["Hangul (Korean) Word Processor File", "Hangul (Korean) Word Processor document", "Hangul Word Processor document", /^Hancom HWP \(Hangul Word Processor\)/, "application/x-hwp", /^fmt\/(1083|1084)( |$)/];
	unsupported = true;
}

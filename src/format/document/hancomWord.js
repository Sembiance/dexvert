import {Format} from "../../Format.js";

export class hancomWord extends Format
{
	name        = "Hancom Word";
	website     = "http://fileformats.archiveteam.org/wiki/HWP";
	ext         = [".hwp"];
	magic       = ["Hangul (Korean) Word Processor File", "Hangul (Korean) Word Processor document"];
	unsupported = true;
}

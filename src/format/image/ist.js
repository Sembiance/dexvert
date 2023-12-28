import {Format} from "../../Format.js";

export class ist extends Format
{
	name       = "Atari Interlaced Studio";
	website    = "http://fileformats.archiveteam.org/wiki/Atari_Interlaced_Studio";
	ext        = [".ist"];
	fileSize   = 17184;
	converters = ["recoil2png"];
}

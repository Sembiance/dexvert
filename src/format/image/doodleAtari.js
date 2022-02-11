import {Format} from "../../Format.js";

export class doodleAtari extends Format
{
	name          = "Doodle Atari";
	website       = "http://fileformats.archiveteam.org/wiki/Doodle_(Atari)";
	ext           = [".doo"];
	fileSize      = 32000;
	matchFileSize = true;
	converters    = ["deark", "recoil2png"];
}

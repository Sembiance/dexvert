import {Format} from "../../Format.js";
import {_PNG_MAGIC} from "./png.js";
import {_JPG_MAGIC} from "./jpg.js";

export class doodleAtari extends Format
{
	name          = "Doodle Atari";
	website       = "http://fileformats.archiveteam.org/wiki/Doodle_(Atari)";
	ext           = [".doo"];
	fileSize      = 32000;
	matchFileSize = true;
	forbiddenMagic = [..._PNG_MAGIC, ..._JPG_MAGIC];
	converters    = ["deark", "recoil2png"];
}

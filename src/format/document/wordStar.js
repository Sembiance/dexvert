import {Format} from "../../Format.js";

export class wordStar extends Format
{
	name       = "WordStar Document";
	website    = "http://fileformats.archiveteam.org/wiki/Wordstar";
	ext        = [".ws", ".ws3", ".ws5", ".ws7", ".ws2", ".wsd"];
	magic      = [/^WordStar .*document$/];
	converters = ["wordStar", "fileMerlin"];
}

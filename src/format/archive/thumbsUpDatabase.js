import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class thumbsUpDatabase extends Format
{
	name       = "ThumbsUp/ThumbsPlus! Database";
	website    = "http://fileformats.archiveteam.org/wiki/ThumbsPlus_database";
	ext        = [".tud"];
	magic      = ["ThumbsUp Database"];
	idCheck    = async inputFile => inputFile.size>=16 && (await fileUtil.readFileBytes(inputFile.absolute, 4, 8)).getUInt32LE()===inputFile.size;
	converters = ["deark[module:thumbsplus"];
}

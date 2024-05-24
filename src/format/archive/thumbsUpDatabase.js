import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class thumbsUpDatabase extends Format
{
	name        = "ThumbsUp Database";
	magic       = ["ThumbsUp Database"];
	idCheck     = async inputFile => inputFile.size>=16 && (await fileUtil.readFileBytes(inputFile.absolute, 4, 8)).getUInt32LE()===inputFile.size;
	unsupported = true;
}

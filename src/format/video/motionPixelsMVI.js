import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class motionPixelsMVI extends Format
{
	name       = "Motion Pixels MVI";
	website    = "https://wiki.multimedia.cx/index.php/Motion_Pixels";
	ext        = [".mvi"];
	idCheck    = async inputFile => inputFile.size>30 && (await fileUtil.readFileBytes(inputFile.absolute, 1))[0]===0x07;
	converters = ["nihav"];
}


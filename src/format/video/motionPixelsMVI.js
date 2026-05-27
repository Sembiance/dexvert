import {Format} from "../../Format.js";

export class motionPixelsMVI extends Format
{
	name       = "Motion Pixels MVI";
	website    = "https://wiki.multimedia.cx/index.php/Motion_Pixels";
	ext        = [".mvi"];
	byteCheck  = [{offset : 0, match : [0x07]}];
	idCheck    = inputFile => inputFile.size>30;
	converters = ["nihav"];
}


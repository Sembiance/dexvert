import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class xbvVideo extends Format
{
	name        = "XBV Video";
	website     = "https://wiki.multimedia.cx/index.php/XBV";
	ext         = [".xbv"];
	magic       = ["XBV video"];
	idCheck    = async inputFile => inputFile.size>=12 && (await fileUtil.readFileBytes(inputFile.absolute, 4, 4)).getUInt32LE()===inputFile.size;
	unsupported = true;
}

import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class packedPFT extends Format
{
	name       = "PACKED/PFT Compressed Archive";
	website    = "http://fileformats.archiveteam.org/wiki/The_Print_Shop";
	ext        = [".pak"];
	magic      = ["PACKED/PFT compressed archive"];
	idCheck    = async inputFile => inputFile.size>2 && (await fileUtil.readFileBytes(inputFile.absolute, 2, -2)).indexOfX([0x1E, 0x00])===0;
	converters = ["packerPFT"];
}

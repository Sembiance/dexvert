import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class zxs extends Format
{
	name         = "ZXS";
	ext          = [".zxs"];
	idCheck      = async inputFile => (await fileUtil.readFileBytes(inputFile.absolute, 1))[0]===0x06;	// every ZXS sample I have starts with 0x06
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul"];
}

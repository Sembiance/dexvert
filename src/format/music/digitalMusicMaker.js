import {xu} from "xu";
import {Format} from "../../Format.js";
import {fileUtil} from "xutil";

export class digitalMusicMaker extends Format
{
	name         = "Digital Music Maker";
	ext          = [".dmm"];
	idCheck      = async inputFile => inputFile.size>13 && (await fileUtil.readFileBytes(inputFile.absolute, 13))[12]===0x40;	// every DMM sample I have has 0x40 as the 13th byte
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;	// due to being an extension only match
}

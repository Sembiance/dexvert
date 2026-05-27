import {xu} from "xu";
import {Format} from "../../Format.js";

export class digitalMusicMaker extends Format
{
	name         = "Digital Music Maker";
	ext          = [".dmm"];
	byteCheck    = [{offset : 12, match : [0x40]}];	// every DMM sample I have has 0x40 as the 13th byte
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123"];
	verify       = ({meta}) => meta.duration>=xu.SECOND;	// due to being an extension only match
}

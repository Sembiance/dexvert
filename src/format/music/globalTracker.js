import {Format} from "../../Format.js";

export class globalTracker extends Format
{
	name         = "Global Tracker";
	ext          = [".gtr"];
	magic        = ["Spectrum Global Tracker chiptune"];
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul[matchType:magic]"];
}

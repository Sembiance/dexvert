import {Format} from "../../Format.js";

export class sqTracker extends Format
{
	name         = "SQ Tracker";
	ext          = [".sqt"];
	magic        = ["SQ Tracker chiptune"];
	weakMagic    = true;
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul[strongMatch]"];
}

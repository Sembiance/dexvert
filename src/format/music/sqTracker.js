import {xu} from "xu";
import {Format} from "../../Format.js";

export class sqTracker extends Format
{
	name         = "SQ Tracker";
	ext          = [".sqt"];
	magic        = ["SQ Tracker chiptune"];
	weakMagic    = true;
	metaProvider = ["musicInfo"];
	converters   = ["zxtune123", "ayEmul[strongMatch]"];
	verify       = ({meta}) => meta.duration>=xu.SECOND*3;	// due to weak magic
}
